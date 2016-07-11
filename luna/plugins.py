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

import collections #For namedtuple.
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

The plug-ins are indexed by tuples as keys, of the form (<type>, <identity>),
where <type> is the plug-in type and <identity> the identifier of the plug-in.
"""

__DependencyCandidate = collections.namedtuple("NamedCandidate", "identity type plugin_class dependencies")
"""
Represents a candidate dependency. We could run the __init__ of this candidate,
but we haven't resolved dependencies yet or instantiated the plug-in object.

This is a named tuple consisting of the following fields:
* identity: An unique identifier for the plug-in.
* type: The plug-in type.
* plugin_class: The class that implements the abstract base class of the
specified plug-in type.
* dependencies: A list of plug-in identities on which this plug-in depends.
"""

def add_plugin_location(location):
	"""
	.. function:: addPluginLocation(location)
	Adds a location to the list of locations where the application looks for
	plug-ins.

	It looks recursively through all subfolders of the specified folder.

	:param location: The location to add to the location list.
	"""
	if not location or not os.path.isdir(location): #Invalid plug-in location.
		raise NotADirectoryError("Plug-in location is not a path: {location}".format(location=location))
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
	candidates = __find_candidates() #Makes a set of (id, path) tuples indicating names and folder paths of possible plug-ins.
	dependency_candidates = [] #Second stage of candidates. We could load these but haven't resolved dependencies yet. List of __DependencyCandidate instances.
	for name, folder in candidates:
		luna.logger.debug("Loading plug-in {plugin} from {folder}.", plugin=name, folder=folder)
		#Loading the plug-in.
		module = __load_candidate(name, folder)
		if not module: #Failed to load module.
			continue

		#Parsing the metadata.
		try:
			metadata = module.metadata()
		except Exception as e:
			luna.logger.warning("Failed to load metadata of plug-in {plugin}: {error_message}", plugin=name, error_message=str(e))
			continue
		if not metadata or not isinstance(metadata, dict): #Metadata not a dictionary.
			luna.logger.warning("Metadata of plug-in {plugin} is not a dictionary. Can't load this plug-in.", plugin=name)
			continue
		if "type" not in metadata:
			luna.logger.warning("Plug-in {plugin} defines no plug-in type. Can't load this plug-in.", plugin=name)
			continue
		if __get_plugin(metadata["type"], name):
			luna.logger.warning("Plug-in {plugin} is already loaded.", plugin=name)
			continue
		if "class" not in metadata:
			luna.logger.warning("Plug-in {plugin} defines no base class. Can't load this plug-in.", plugin=name)
			continue
		try:
			int(metadata["class"].APIVERSION)
		except AttributeError:
			luna.logger.warning("Plug-in {plugin} specifies a class {plugin_class} that is not a subclass of Plugin. Can't load this plug-in.", plugin=name, plugin_class=str(metadata["class"]))
			continue
		if "apiVersions" not in metadata:
			luna.logger.warning("Metadata of plug-in {plugin} has no API version number. Can't load this plug-in.", plugin=name)
			continue
		if not isinstance(metadata["apiVersions"], dict):
			luna.logger.warning("The API version numbers of plug-in {plugin} is not a dictionary. Can't load this plug-in.", plugin=name)
			continue
		correct_api_version_numbers = True
		for key, value in metadata["apiVersions"].items(): #Check if the API version number of each plug-in type is within range.
			try:
				min_api_version, max_api_version = value
			except TypeError:
				luna.logger.warning("Plug-in {plugin} requires an API version number range {range} for {plugin_type} type plug-ins, but it must be a tuple indicating the minimum and maximum version number.", plugin=name, range=str(value), plugin_type=key.__name__)
				correct_api_version_numbers = False
				break #Continue the outer loop.
			try:
				if key.APIVERSION < min_api_version or key.APIVERSION > max_api_version:
					luna.logger.warning("Plug-in {plugin} requires an API version number between {minimum} and {maximum} for {plugin_type} type plug-ins, but the current version number is {version}.", plugin=name, minimum=min_api_version, maximum=max_api_version, plugin_type=key.__name__, version=key.APIVERSION)
					correct_api_version_numbers = False
					break #Continue the outer loop.
			except TypeError:
				luna.logger.warning("Plug-in {plugin} specifies a required API version number for {plugin_type} type plug-ins that is not a number.", plugin=name, plugin_type=key.__name__)
				correct_api_version_numbers = False
				break #Continue the outer loop.
			except AttributeError: #The key.APIVERSION went wrong.
				luna.logger.warning("Plug-in {plugin} specifies allowed API version numbers for type {plugin_type}, which is not a plug-in class.", plugin=name, plugin_type=str(key))
				correct_api_version_numbers = False
				break #Continue the outer loop.
		if not correct_api_version_numbers:
			continue
		dependencies = [] #If this entry is missing, give a warning but assume that there are no dependencies.
		if "dependencies" in metadata:
			dependencies = metadata["dependencies"]
		else:
			luna.logger.warning("Plug-in {plugin} defines no dependencies. Assuming it has no dependencies.", plugin=name)

		dependency_candidates.append(__DependencyCandidate(identity=name, type=metadata["type"], plugin_class=metadata["class"], dependencies=dependencies))

	#Now go through the candidates to find plug-ins for which we can resolve the dependencies.
	for candidate in dependency_candidates:
		for dependency in candidate.dependencies:
			if dependency.count("/") != 1:
				luna.logger.warning("Plug-in {plugin} has an invalid dependency {dependency}.", plugin=candidate.identity, dependency=dependency)
				continue #With the next dependency.
			dependency_type, dependency_name = dependency.split("/", 1) #Parse the dependency.
			for dependency_candidate in dependency_candidates:
				if dependency_name == dependency_candidate.name and dependency_type == dependency_candidate.type:
					break
			else: #Dependency was not found.
				luna.logger.warning("Plug-in {plugin} is missing dependency {dependency}!", plugin=candidate.identity, dependency=dependency_name)
				break
		else: #All dependencies are resolved!
			try:
				plugin_instance = candidate.plugin_class() #Actually construct an instance of the plug-in.
			except Exception as e:
				luna.logger.warning("Initialising plug-in {plugin} failed: {error_message}", plugin=candidate.itentity, error_message=str(e))
				continue #With next plug-in.
			__plugins[(candidate.type, candidate.identity)] = plugin_instance

def get_interface(name):
	"""
	.. function:: getInterface(name)
	Gets an interface plug-in with the specified name, if it exists.

	:param name: The name of the interface plug-in to get.
	:returns: The specified interface, or ``None`` if it doesn't exist.
	"""
	return __get_plugin("interface", name)

def get_interfaces():
	"""
	.. function:: getInterfaces()
	Gets all interface plug-ins.

	:returns: A list of all interface plug-ins.
	"""
	return __get_all_plugins_of_type("interface")

def get_logger(name):
	"""
	.. function:: getLogger(name)
	Gets a logger plug-in with the specified name, if it exists.

	:param name: The name of the logger plug-in to get.
	:returns: The specified logger, or ``None`` if it doesn't exist.
	"""
	return __get_plugin("logger", name)

def get_loggers():
	"""
	.. function:: getLoggers()
	Gets all logger plug-ins.

	:returns: A list of all logger plug-ins.
	"""
	return __get_all_plugins_of_type("logger")

def __find_candidates():
	"""
	.. function:: __findCandidates()
	Finds candidates for what looks like might be plug-ins.

	A candidate is a folder inside a plug-in location, which has a file
	``__init__.py``. The file is not yet executed at this point.

	:returns: A set of tuples of the form (<name>, <path>), containing
	respectively the name of the plug-in and the path to the plug-in's folder.
	"""
	candidates = set()
	for location in __plugin_locations:
		for root, directories, files in os.walk(location, followlinks=True):
			if "__init__.py" not in files: #The directory must have an __init__.py file.
				continue
			directories[:] = [] #Remove all subdirectories. We aren't going to look in submodules.
			identity = os.path.basename(root) #The name of the folder becomes the plug-in's identity.
			candidates.add((identity, location))
	return candidates

def __load_candidate(name, folder):
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
		luna.logger.warning("Can't load plug-in {plugin}: Invalid plug-in name; periods are forbidden.", plugin=name)
		return None
	try:
		file, path, description = imp.find_module(name, [folder])
	except Exception as e:
		luna.logger.warning("Failed to find module of plug-in in {plugin}: {error_message}", plugin=folder, error_message=str(e))
		return None
	try:
		module = imp.load_module(name, file, path, description)
	except Exception as e:
		luna.logger.warning("Failed to load plug-in {plugin}: {error_message}", plugin=name, error_message=str(e))
		raise
	finally:
		if file: #Plug-in loading should not open any files, but if it does, close it immediately.
			luna.logger.warning("Plug-in {plugin} is a file: {filename}", plugin=name, filename=str(file))
			file.close()
	return module

def __get_all_plugins_of_type(plugin_type):
	"""
	.. function:: __getAllPluginsOfType(type)
	Gets all plug-ins with the specified type.

	:returns: A list of all plug-ins of the specified plug-in type.
	"""
	result = []
	for (candidate_type, candidate_name) in __plugins:
		if plugin_type == candidate_type:
			result.append(__plugins[(candidate_type, candidate_name)])
	return result

def __get_plugin(plugin_type, name):
	"""
	.. function:: __getPlugin(type, name)
	Gets a plug-in of the specified type and the specified name, if it
	exists.

	:param type: The plug-in type of the plug-in to get.
	:param name: The name of the plug-in to get.
	:returns: The plug-in, or ``None`` if it doesn't exist.
	"""
	if (plugin_type, name) in __plugins:
		return __plugins[(plugin_type, name)]
	return None #Plug-in couldn't be found.