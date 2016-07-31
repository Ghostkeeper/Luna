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

__required_metadata_fields = {"dependencies", "description", "name", "version"}
"""
Fields that must be present in every plug-in's metadata.
"""

__UnresolvedCandidate = collections.namedtuple("__UnresolvedCandidate", "identity metadata dependencies")
"""
Represents a candidate plug-in whose dependencies haven't yet been resolved.

We could run the __init__ of this candidate and get its metadata, but we haven't
resolved dependencies yet or registered the plug-in with its type.

This is a named tuple consisting of the following fields:
* identity: An unique identifier for the plug-in.
* metadata: The metadata of the plug-in.
* dependencies: A list of plug-in identities on which this plug-in depends.
"""

__PluginType = collections.namedtuple("__PluginType", "api register validate_metadata")
"""
Represents a plug-in type plug-in.

This is a named tuple consisting of the following fields:
* api: The class that provides the API for the plug-ins of this type.
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

def api(plugin_type):
	"""
	.. function:: api(plugin_type)
	Gets the API to interact with plug-ins of the specified type.

	These APIs provide sets of functions to interact with the plug-ins of that
	type. Some API calls may invoke actions on multiple plug-ins at once, or
	just on a specific one. For details on the API of a specific plug-in type,
	please refer to the plug-in that defines the type.

	:param plugin_type: The plug-in type to get the API of.
	:return: An object with methods to interact with plug-ins of the specified
		type.
	:raises ImportError The plug-in type is unknown.
	"""
	if plugin_type not in __plugin_types:
		raise ImportError("No API known for \"{type}\".".format(type=plugin_type))
	return __plugin_types[plugin_type].api

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
	unvalidated_candidates = [] #Second stage of candidates. We could load these but haven't validated their typed metadata yet. List of __UnresolvedCandidate instances.
	for identity, folder in candidates:
		#Loading the plug-in.
		module = __load_candidate(identity, folder)
		if not module: #Failed to load module.
			continue

		#Parsing the metadata.
		try:
			metadata = module.metadata()
		except Exception as e:
			try:
				api("logger").warning("Failed to load metadata of plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
			except ImportError: #Logger type hasn't loaded yet.
				print("Failed to load metadata of plug-in {plugin}: {error_message}".format(plugin=identity, error_message=str(e)))
			continue
		try:
			__validate_metadata_global(metadata)
		except MetadataValidationError as e:
			try:
				api("logger").warning("Metadata of plug-in {plugin} is invalid: {error_message}", plugin=identity, error_message=str(e))
			except ImportError: #Logger type hasn't loaded yet.
				print("Metadata of plug-in {plugin} is invalid: {error_message}".format(plugin=identity, error_message=str(e)))
			continue
		if "type" in metadata: #For plug-in type definitions, we have a built-in metadata checker.
			try:
				__validate_metadata_type(metadata)
			except MetadataValidationError as e:
				try:
					api("logger").warning("Metadata of type plug-in {plugin} is invalid: {error_message}", plugin=identity, error_message=str(e))
				except ImportError: #Logger type hasn't loaded yet.
					print("Metadata of type plug-in {plugin} is invalid: {error_message}".format(plugin=identity, error_message=str(e)))
				continue
			plugin_type = __PluginType(api=metadata["type"]["api"], register=metadata["type"]["register"], validate_metadata=metadata["type"]["validate_metadata"])
			__plugin_types[metadata["type"]["type_name"]] = plugin_type

		unvalidated_candidates.append(__UnresolvedCandidate(identity=identity, metadata=metadata, dependencies=metadata["dependencies"])) #Goes on to the second stage.

	unresolved_candidates = [] #Third stage of candidates. We could validate their metadata but haven't resolved their dependencies yet. List of __UnresolvedCandidate instances.
	for candidate in unvalidated_candidates:
		candidate_types = candidate.metadata.keys() & __plugin_types.keys() #The plug-in types this candidate proposes to implement.
		for candidate_type in candidate_types:
			try:
				__plugin_types[candidate_type].validate_metadata(candidate.metadata)
			except Exception as e:
				api("logger").warning("Could not validate {candidate} as a plug-in of type {type}: {error_message}", candidate=candidate.identity, type=candidate_type, error_message=str(e))
				break #Do not load this plug-in, even if other types may be valid! That could cause plug-ins to get their dependencies resolved while those dependencies don't have valid metadata.
		else: #All types got validated properly.
			unresolved_candidates.append(candidate) #Goes on to the third stage.

	#Now go through the candidates to find plug-ins for which we can resolve the dependencies.
	for candidate in unresolved_candidates:
		for dependency, requirements in candidate.dependencies.items():
			for dependency_candidate in unresolved_candidates:
				if dependency == dependency_candidate.identity:
					if not __meets_requirements(dependency_candidate.metadata, requirements, dependency, candidate):
						continue #Search on.
					else:
						break #Found this dependency.
			else: #Dependency was not found.
				api("logger").warning("Plug-in {plugin} is missing dependency {dependency}.", plugin=candidate.identity, dependency=dependency)
				break
		else: #All dependencies are resolved!
			candidate_types = candidate.metadata.keys() & __plugin_types.keys() #The plug-in types to register the plug-in at.
			for candidate_type in candidate_types:
				try:
					__plugin_types[candidate_type].register(candidate.identity, candidate.metadata)
				except Exception as e:
					api("logger").error("Couldn't register plug-in {candidate} as type {type}: {error_message}", candidate=candidate.identity, type=candidate_type, error_message=str(e))
					#Cannot guarantee that dependencies have been met now. But still continue to try to register as many other types as possible.
			api("logger").info("Loaded plug-in {plugin}.", plugin=candidate.identity)

def __meets_requirements(candidate_metadata, requirements, candidate_identity, depending_identity):
	"""
	.. function:: __meets_requirements(candidate_metadata, requirements, candidate_identity, depending_identity)
	Checks whether a candidate meets the requirements set by a dependant
	plug-in.

	The requirements dictionary has a few specific things that can be checked
	for:
	* ``version_min``: The minimum allowed version of the candidate.
	* ``version_max``: The maximum allowed version of the candidate.

	If a candidate doesn't meet the requirements, a warning is put in the log
	and the method returns ``False``.

	:param candidate_metadata: The metadata dictionary of a candidate dependency
		of the plug-in.
	:param requirements: The requirements set by a plug-in that depends on the
		candidate.
	:param candidate_identity: The identity of the candidate. Used for logging.
	:param depending_identity: The identity of the plug-in that depends on the
		candidate. Used for logging.
	:return: ``True`` if the candidate meets the requirements, or ``False`` if
		it doesn't.
	"""
	#Minimum version requirement.
	try:
		if "version_min" in requirements and candidate_metadata["version"] < requirements["version_min"]:
			api("logger").warning("Plug-in {plugin} requires {dependency} version {version_min} or later.", plugin=depending_identity, dependency=candidate_identity, version_min=str(requirements["version_min"]))
			return False
	except TypeError: #Unorderable types.
		api("logger").warning("Plug-in {plugin} requires {dependency} version {version_min} or later, but couldn't compare this with its actual version {version}.", plugin=depending_identity, dependency=candidate_identity, version_min=str(requirements["version_min"], version=str(candidate_metadata["version"])))
		return False

	#Maximum version requirement.
	try:
		if "version_max" in requirements and candidate_metadata["version"] > requirements["version_max"]:
			api("logger").warning("Plug-in {plugin} requires {dependency} version {version_max} or earlier.", plugin=depending_identity, dependency=candidate_identity, version_max=str(requirements["version_max"]))
			return False
	except TypeError: #Unorderable types.
		api("logger").warning("Plug-in {plugin} requires {dependency} version {version_max} or earlier, but couldn't compare this with its actual version {version}.", plugin=depending_identity, dependency=candidate_identity, version_max=str(requirements["version_max"], version=str(candidate_metadata["version"])))
		return False

	return True

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
			directory = os.path.dirname(root) #The location where the package is located.
			candidates.add((identity, directory))
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
		try:
			api("logger").warning("Can't load plug-in {plugin}: Invalid plug-in identity; periods are forbidden.", plugin=identity)
		except ImportError: #Logger type module isn't loaded yet.
			print("Can't load plug-in {plugin}: Invalid plug-in identity; periods are forbidden.".format(plugin=identity))
		return None
	try:
		file, path, description = imp.find_module(identity, [folder])
	except Exception as e:
		try:
			api("logger").warning("Failed to find module of plug-in in {plugin}: {error_message}", plugin=identity, error_message=str(e))
		except ImportError: #Logger type module isn't loaded yet.
			print("Failed to find module of plug-in in {plugin}: {error_message}".format(plugin=identity, error_message=str(e)))
		return None
	try:
		module = imp.load_module(identity, file, path, description)
	except Exception as e:
		try:
			api("logger").warning("Failed to load plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
		except ImportError: #Logger type module isn't loaded yet.
			print("Failed to load plug-in {plugin}: {error_message}".format(plugin=identity, error_message=str(e)))
		return None
	finally:
		if file: #Plug-in loading should not open any files, but if it does, close it immediately.
			try:
				api("logger").warning("Plug-in {plugin} is a file: {filename}", plugin=identity, filename=str(file))
			except ImportError: #Logger type module isn't loaded yet.
				print("Plug-in {plugin} is a file: {filename}", plugin=identity, filename=str(file))
			file.close()
	return module

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
	allowed_requirements = {"version_max", "version_min"}
	try:
		if not __required_metadata_fields <= metadata.keys(): #Set boolean comparison: Not all required_fields in metadata.
			raise MetadataValidationError("Required fields missing: " + str(__required_metadata_fields - metadata.keys()))
		for requirements in metadata["dependencies"].values(): #Raises AttributeError if not a dictionary.
			if not requirements.keys() <= allowed_requirements:
				raise MetadataValidationError("Unknown plug-in dependency requirements {requirements}.".format(requirements=", ".join(requirements.keys() - allowed_requirements)))
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
		required_fields = {"type_name", "api", "register", "validate_metadata"}
		if not required_fields <= metadata["type"].keys(): #Set boolean comparison: Not all required_fields in metadata["type"].
			raise MetadataValidationError("Required fields in type missing: " + str(required_fields - metadata["type"].keys()))
		if not callable(metadata["type"]["register"]):
			raise MetadataValidationError("The register must be callable.")
		if metadata["type"]["register"].__code__.co_argcount != 2:
			raise MetadataValidationError("The register function must take exactly two arguments: The plug-in's identity and its metadata.")
		if not callable(metadata["type"]["validate_metadata"]):
			raise MetadataValidationError("The metadata validator must be callable.")
		if metadata["type"]["validate_metadata"].__code__.co_argcount != 1:
			raise MetadataValidationError("The metadata validation function must take exactly one argument: The plug-in's metadata.")
		if metadata["dependencies"]:
			raise MetadataValidationError("Type plug-ins may not have dependencies.")
	except (AttributeError, TypeError):
		raise MetadataValidationError("The type section is not a dictionary.")