#!/usr/bin/env python

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
#software, either in source code form or as a compiled binary, for any purpose,
#commercial or non-commercial, and by any means.
#
#In jurisdictions that recognise copyright laws, the author or authors of this
#software dedicate any and all copyright interest in the software to the public
#domain. We make this dedication for the benefit of the public at large and to
#the detriment of our heirs and successors. We intend this dedication to be an
#overt act of relinquishment in perpetuity of all present and future rights to
#this software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <https://unlicense.org/>.

"""
Handles all administration on plug-ins.
"""

import imp #Imports Python modules dynamically.
import os #To search through folders to find the plug-ins.
import luna.logger #Logging messages.

__plugin_locations = []
"""
List of directories where to look for plug-ins.
"""

__plugins = {}
"""
Dictionary holding all plug-ins.

The plug-ins are indexed by tuples as keys, of the form (<type>, <name>),
where <type> is the plug-in type and <name> the identifier of the plug-in.
"""

def addPluginLocation(location):
	"""
	.. function:: addPluginLocation(location)
	Adds a location to the list of locations where the application looks for
	plug-ins.

	:param location: The location to add to the location list.
	"""
	global __plugin_locations
	if location:
		__plugin_locations.append(location)

def discover():
	"""
	.. function:: discover()
	Discovers all plug-ins it can find.

	This goes through all folders of all plug-in types, and finds out what
	their metadata is. If the metadata is correct it will create a plug-in.
	When all plug-ins are loaded, the plug-ins whose dependencies can be met
	will be stored for later requesting. The plug-ins whose dependencies
	cannot be met will be discarded.

	This method can also be used to update the plug-in repository, but
	plug-ins are not deleted then. Only new plug-ins are added by this
	function.
	"""
	candidates = __findCandidates() #Makes a list of (id, path) tuples indicating names and folder paths of possible plug-ins.
	dependency_candidates = [] #Second stage of candidates. We could load these but haven't resolved dependencies yet. Tuples of (name, type, class, dependencies).
	for name, folder in candidates:
		luna.logger.debug("Loading plug-in {plugin} from {folder}.", plugin = name, folder = folder)
		#Loading the plug-in.
		module = __loadCandidate(name, folder)
		if not module: #Failed to load module.
			continue

		#Parsing the metadata.
		try:
			metadata = module.metadata()
		except Exception as e:
			luna.logger.warning("Failed to load metadata of plug-in {plugin}: {error_message}", plugin = name, error_message = str(e))
			continue
		if not metadata or not isinstance(metadata, dict): #Metadata not a dictionary.
			luna.logger.warning("Metadata of plug-in {plugin} is not a dictionary. Can't load this plug-in.", plugin = name)
			continue
		if not "type" in metadata:
			luna.logger.warning("Plug-in {plugin} defines no plug-in type. Can't load this plug-in.", plugin = name)
			continue
		if __getPlugin(metadata["type"], name):
			luna.logger.warning("Plug-in {plugin} is already loaded.", plugin = name)
			continue
		if not "class" in metadata:
			luna.logger.warning("Plug-in {plugin} defines no base class. Can't load this plug-in.", plugin = name)
			continue
		try:
			int(metadata["class"].APIVERSION)
		except:
			luna.logger.warning("Plug-in {plugin} specifies a class {plugin_class} that is not a subclass of Plugin. Can't load this plug-in.", plugin = name, plugin_class = str(metadata["class"]))
			continue
		if not "apiVersions" in metadata:
			luna.logger.warning("Metadata of plug-in {plugin} has no API version number. Can't load this plug-in.", plugin = name)
			continue
		if not isinstance(metadata["apiVersions"], dict):
			luna.logger.warning("The API version numbers of plug-in {plugin} is not a dictionary. Can't load this plug-in.", plugin = name)
			continue
		correct_api_version_numbers = True
		for key, value in metadata["apiVersions"].items(): #Check if the API version number of each plug-in type is within range.
			try:
				min_api_version, max_api_version = value
			except TypeError:
				luna.logger.warning("Plug-in {plugin} requires an API version number range {range} for {plugin_type} type plug-ins, but it must be a tuple indicating the minimum and maximum version number.", plugin = name, range = str(value), plugin_type = key.__name__)
				correct_api_version_numbers = False
				break #Continue the outer loop.
			try:
				if key.APIVERSION < min_api_version or key.APIVERSION > max_api_version:
					luna.logger.warning("Plug-in {plugin} requires an API version number between {minimum} and {maximum} for {plugin_type} type plug-ins, but the current version number is {version}.", plugin = name, minimum = min_api_version, maximum = max_api_version, plugin_type = key.__name__, version = key.APIVERSION)
					correct_api_version_numbers = False
					break #Continue the outer loop.
			except TypeError:
				luna.logger.warning("Plug-in {plugin} specifies a required API version number for {plugin_type} type plug-ins that is not a number.", plugin = name, plugin_type = key.__name__)
				correct_api_version_numbers = False
				break #Continue the outer loop.
			except AttributeError: #The key.APIVERSION went wrong.
				luna.logger.warning("Plug-in {plugin} specifies allowed API version numbers for type {plugin_type}, which is not a plug-in class.", plugin = name, plugin_type = str(key))
				correct_api_version_numbers = False
				break #Continue the outer loop.
		if not correct_api_version_numbers:
			continue
		dependencies = [] #If this entry is missing, give a warning but assume that there are no dependencies.
		if "dependencies" in metadata:
			dependencies = metadata["dependencies"]
		else:
			luna.logger.warning("Plug-in {plugin} defines no dependencies. Assuming it has no dependencies.", pluginType = name)

		dependency_candidates.append((name, metadata["type"], metadata["class"], dependencies, module))

	#Now go through the candidates to find plug-ins for which we can resolve the dependencies.
	global __plugins
	for plugin_name, plugin_type, plugin_class, plugin_dependencies, plugin_module in dependency_candidates:
		for dependency in plugin_dependencies:
			if dependency.count("/") != 1:
				luna.logger.warning("Plug-in {plugin} has an invalid dependency {dependency}.", plugin = plugin_name, dependency = dependency)
				continue #With the next dependency.
			dependency_type, dependency_name = dependency.split("/", 1) #Parse the dependency.
			for dependency_candidate_name, dependency_candidate_type, _, _, _ in dependency_candidates: #See if that dependency is present.
				if dependency_name == dependency_candidate_name and dependency_type == dependency_candidate_type:
					break
			else: #Dependency was not found.
				luna.logger.warning("Plug-in {plugin} is missing dependency {dependency}!", plugin = plugin_name, dependency = dependency)
				break
		else: #All dependencies are resolved!
			try:
				plugin_instance = plugin_class() #Actually construct an instance of the plug-in.
			except Exception as e:
				luna.logger.warning("Initialising plug-in {plugin} failed: {error_message}", plugin = plugin_name, error_message = str(e))
				continue #With next plug-in.
			__plugins[(plugin_type, plugin_name)] = plugin_instance

def getInterface(name):
	"""
	.. function:: getInterface(name)
	Gets an interface plug-in with the specified name, if it exists.

	:param name: The name of the interface plug-in to get.
	:returns: The specified interface, or ``None`` if it doesn't exist.
	"""
	return __getPlugin("interface", name)

def getInterfaces():
	"""
	.. function:: getInterfaces()
	Gets all interface plug-ins.

	:returns: A list of all interface plug-ins.
	"""
	return __getAllPluginsOfType("interface")

def getLogger(name):
	"""
	.. function:: getLogger(name)
	Gets a logger plug-in with the specified name, if it exists.

	:param name: The name of the logger plug-in to get.
	:returns: The specified logger, or ``None`` if it doesn't exist.
	"""
	return __getPlugin("logger", name)

def getLoggers():
	"""
	.. function:: getLoggers()
	Gets all logger plug-ins.

	:returns: A list of all logger plug-ins.
	"""
	return __getAllPluginsOfType("logger")

def __findCandidates():
	"""
	.. function:: __findCandidates()
	Finds candidates for what looks like might be plug-ins.

	A candidate is a folder inside a plug-in location, which has a file
	``__init__.py``. The file is not yet executed at this point.

	:returns: A list of tuples of the form (<name>, <path>), containing
		respectively the name of the plug-in and the path to the plug-in's
		folder.
	"""
	global __plugin_locations
	candidates = []
	for location in __plugin_locations:
		if not os.path.isdir(location): #Invalid plug-in location.
			luna.logger.warning("Plug-in location not valid: {location}", location = location)
			continue
		for plugin_folder in os.listdir(location):
			name = plugin_folder #The name of the folder becomes the plug-in's actual name.
			plugin_folder = os.path.join(location, plugin_folder)
			if not os.path.isdir(plugin_folder): #os.listdir gets both files and folders. We want only folders at this level.
				continue
			init_script = os.path.join(plugin_folder, "__init__.py") #Plug-in must have an init script.
			if os.path.exists(init_script) and (os.path.isfile(init_script) or os.path.islink(init_script)):
				candidates.append((name, location))
	return candidates

def __loadCandidate(name, folder):
	"""
	.. function:: __loadCandidate(name, folder)
	Loads a plug-in candidate as a Python package.

	This is intended to be used on Python packages, containing an init
	script.

	:param name: The name of the plug-in to load. Hierarchical names are not
		supported.
	:param folder: The path to the folder where the plug-in can be found.
	:returns: A Python package representing the plug-in. If anything went
		wrong, ``None`` is returned.
	"""
	if "." in name:
		luna.logger.warning("Can't load plug-in {plugin}: Invalid plug-in name; periods are forbidden.", plugin = name)
		return None
	try:
		file, path, description = imp.find_module(name, [folder])
	except Exception as e:
		luna.logger.warning("Failed to find module of plug-in in {plugin}: {error_message}", plugin = folder, error_message = str(e))
		return None
	try:
		module = imp.load_module(name, file, path, description)
	except Exception as e:
		luna.logger.warning("Failed to load plug-in {plugin}: {error_message}", plugin = name, error_message = str(e))
		raise e
		return None
	finally:
		if file: #Plug-in loading should not open any files, but if it does, close it immediately.
			luna.logger.warning("Plug-in {plugin} is a file: {filename}", plugin = name, filename = str(file))
			file.close()
	return module

def __getAllPluginsOfType(type):
	"""
	.. function:: __getAllPluginsOfType(type)
	Gets all plug-ins with the specified type.

	:returns: A list of all plug-ins of the specified plug-in type.
	"""
	global __plugins
	result = []
	for (candidate_type, candidate_name) in __plugins:
		if type == candidate_type:
			result.append(__plugins[(candidate_type, candidate_name)])
	return result

def __getPlugin(type, name):
	"""
	.. function:: __getPlugin(type, name)
	Gets a plug-in of the specified type and the specified name, if it
	exists.

	:param type: The plug-in type of the plug-in to get.
	:param name: The name of the plug-in to get.
	:returns: The plug-in, or ``None`` if it doesn't exist.
	"""
	global __plugins
	if (type, name) in __plugins:
		return __plugins[(type, name)]
	return None #Plug-in couldn't be found.