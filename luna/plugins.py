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
import luna.plugin #Checking if plug-ins provide the correct class.

__plugin_locations = []
"""
List of directories where to look for plug-ins.
"""

__plugin_types = {}
"""
Dictionary of all plug-in types.

The keys are the type names of the plug-in types. The values are the plug-in
types as named tuples.
"""

__plugins = {}
"""
Dictionary holding all plug-ins, indexed by their identity.
"""

__DependencyCandidate = collections.namedtuple("__DependencyCandidate", "identity metadata dependencies")
"""
Represents a candidate dependency.

We could run the __init__ of this candidate, but we haven't resolved
dependencies yet or instantiated the plug-in object.

This is a named tuple consisting of the following fields:
* identity: An unique identifier for the plug-in.
* metadata: The metadata of the plug-in.
* dependencies: A list of plug-in identities on which this plug-in depends.
"""

__PluginType = collections.namedtuple("__PluginType", "api interface register validate_metadata")
"""
Represents a plug-in type plug-in.

This is a named tuple consisting of the following fields:
* api: The class that provides the API for the plug-ins of this type.
* interface: The interface that plug-ins of this type must implement.
* register: The function that plug-ins of this type must register with.
* validate_metadata: The function that verifies that the metadata is valid for
this type.
"""

class MetadataValidationError(Exception):
	"""
	Marker exception to indicate that the metadata of a plug-in is invalid.
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
	for identity, folder in candidates:
		luna.logger.debug("Loading plug-in {plugin} from {folder}.", plugin=identity, folder=folder)
		#Loading the plug-in.
		module = __load_candidate(identity, folder)
		if not module: #Failed to load module.
			continue
		if __get_plugin(identity):
			luna.logger.warning("Plug-in {plugin} is already loaded.", plugin=identity)
			continue

		#Parsing the metadata.
		try:
			metadata = module.metadata()
		except Exception as e:
			luna.logger.warning("Failed to load metadata of plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
			continue
		try:
			__validate_metadata_global(metadata)
		except MetadataValidationError as e:
			luna.logger.warning("Metadata of plug-in {plugin} is invalid: {message}", plugin=identity, message=str(e))
			continue
		if "type" in metadata: #For plug-in type definitions, we have a built-in metadata checker.
			try:
				__validate_metadata_type(metadata)
			except MetadataValidationError as e:
				luna.logger.warning("Metadata of type plug-in {plugin} is invalid: {message}", plugin=identity, message=str(e))
				continue
			plugin_type = __PluginType(**metadata["type"]) #All metadata for type maps directly to this named tuple.
			self.__plugin_types[metadata["type_name"]] = plugin_type

		dependency_candidates.append(__DependencyCandidate(identity=identity, metadata=metadata, dependencies=dependencies))

	#Now go through the candidates to find plug-ins for which we can resolve the dependencies.
	for candidate in dependency_candidates:
		for dependency in candidate.dependencies:
			if dependency.count("/") != 1:
				luna.logger.warning("Plug-in {plugin} has an invalid dependency {dependency}.", plugin=candidate.identity, dependency=dependency)
				continue #With the next dependency.
			dependency_type, dependency_identity = dependency.split("/", 1) #Parse the dependency.
			for dependency_candidate in dependency_candidates:
				if dependency_identity == dependency_candidate.identity and dependency_type == dependency_candidate.type:
					break
			else: #Dependency was not found.
				luna.logger.warning("Plug-in {plugin} is missing dependency {dependency}!", plugin=candidate.identity, dependency=dependency_identity)
				break
		else: #All dependencies are resolved!
			try:
				plugin_instance = candidate.plugin_class() #Actually construct an instance of the plug-in.
			except Exception as e:
				luna.logger.warning("Initialising plug-in {plugin} failed: {error_message}", plugin=candidate.itentity, error_message=str(e))
				continue #With next plug-in.
			__plugins[candidate.identity] = plugin_instance

def get_interface(name):
	"""
	.. function:: getInterface(name)
	Gets an interface plug-in with the specified name, if it exists.

	:param name: The name of the interface plug-in to get.
	:returns: The specified interface, or ``None`` if it doesn't exist.
	"""
	return __get_plugin(name)

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
	return __get_plugin(name)

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

	:returns: A set of tuples of the form (<identity>, <path>), containing
	respectively the identity of the plug-in and the path to the plug-in's
	folder.
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

def __load_candidate(identity, folder):
	"""
	.. function:: __loadCandidate(identity, folder)
	Loads a plug-in candidate as a Python package.

	This is intended to be used on Python packages, containing an init
	script.

	:param identity: The identity of the plug-in to load. Hierarchical
		identities are not supported.
	:param folder: The path to the folder where the plug-in can be found.
	:returns: A Python package representing the plug-in. If anything went
		wrong, ``None`` is returned.
	"""
	if "." in identity:
		luna.logger.warning("Can't load plug-in {plugin}: Invalid plug-in identity; periods are forbidden.", plugin=identity)
		return None
	try:
		file, path, description = imp.find_module(identity, [folder])
	except Exception as e:
		luna.logger.warning("Failed to find module of plug-in in {plugin}: {error_message}", plugin=folder, error_message=str(e))
		return None
	try:
		module = imp.load_module(identity, file, path, description)
	except Exception as e:
		luna.logger.warning("Failed to load plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
		raise
	finally:
		if file: #Plug-in loading should not open any files, but if it does, close it immediately.
			luna.logger.warning("Plug-in {plugin} is a file: {filename}", plugin=identity, filename=str(file))
			file.close()
	return module

def __get_all_plugins_of_type(plugin_type):
	"""
	.. function:: __getAllPluginsOfType(type)
	Gets all plug-ins with the specified type.

	:returns: A list of all plug-ins of the specified plug-in type.
	"""
	result = []
	for (candidate_type, candidate_identity) in __plugins:
		if plugin_type == candidate_type:
			result.append(__plugins[(candidate_type, candidate_identity)])
	return result

def __get_plugin(identity):
	"""
	.. function:: __getPlugin(identity)
	Gets the plug-in with the specified identity, if it exists.

	:param identity: The identity of the plug-in to get.
	:returns: The plug-in, or ``None`` if it doesn't exist.
	"""
	if identity in __plugins:
		return __plugins[identity]
	return None #Plug-in couldn't be found.

def __validate_metadata_global(metadata):
	"""
	.. function:: __validate_metadata_global(metadata)
	Checks if the global part of the metadata of a plug-in is correct.

	If it is incorrect, an exception is raised.

	The global part of the metadata includes the part of metadata that is common
	among all plug-ins.

	:param metadata: A dictionary containing the metadata of the plug-in.
	:raises MetadataValidationError: The metadata is invalid.
	"""
	required_fields = {"name", "description", "version", "class"}
	try:
		if not required_fields <= metadata.keys(): #Set boolean comparison: Not all required_fields in metadata.
			raise MetadataValidationError("Required fields missing: " + str(required_fields - metadata.keys()))
		if not issubclass(metadata["class"], luna.plugin.Plugin):
			raise MetadataValidationError("The plug-in class is not a subclass of luna.plugin.Plugin.")
	except (AttributeError, TypeError):
		raise MetadataValidationError("Metadata is not a dictionary.")

def __validate_metadata_type(metadata):
	"""
	.. function:: __validate_metadata_type(metadata)
	Checks if the metadata of a plug-in type plug-in is correct.

	If it is incorrect, an exception is raised. At this point, the metadata must
	already be validated as plug-in metadata.

	:param metadata: A dictionary containing the metadata of the plug-in.
	:raises MetadataValidationError: The metadata is invalid.
	"""
	if "type" not in metadata:
		raise MetadataValidationError("This is not a plug-in type plug-in.")
	try:
		required_fields = {"type_name", "api", "interface", "register", "validate_metadata"}
		if not required_fields <= metadata["type"].keys(): #Set boolean comparison: Not all required_fields in metadata["type"].
			raise MetadataValidationError("Required fields in type missing: " + str(required_fields - metadata["type"].keys()))
		if not "_abc_registry" in dir(metadata["type"]["interface"]):
			raise MetadataValidationError("The interface must be an abstract base class.")
		if not callable(metadata["type"]["register"]):
			raise MetadataValidationError("The register must be callable.")
		if not callable(metadata["type"]["validate_metadata"]):
			raise MetadataValidationError("The metadata validator must be callable.")
		if metadata["dependencies"]:
			raise MetadataValidationError("Type plug-ins may not have dependencies.")
	except (AttributeError, TypeError):
		raise MetadataValidationError("The type section is not a dictionary.")