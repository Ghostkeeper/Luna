#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Handles all administration on plug-ins.
"""

import collections #For namedtuple.
import imp #Imports Python modules dynamically.
import logging #Fallback logging for if the logger plug-ins aren't loaded yet.
import os #To search through folders to find the plug-ins.
import sys #Make fallback logger output to stdout instead of stderr.

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO, stream=sys.stdout) #Set the fallback log level to the default for the application.

_plugin_locations = []
"""
List of directories where to look for plug-ins.
"""

_plugin_types = {}
"""
Dictionary of all plug-in types.

The keys are the type names of the plug-in types. The values are the plug-in
types as named tuples.
"""

_plugins = {}
"""
All plug-ins, by their identities.

This also includes all plug-ins that are not registered.
"""

plugins_by_type = {}
"""
All plug-ins, indexed by their types.

This is the main index of registered plug-ins. Each entry contains a set of
plug-in identities. Note that a plug-in may have multiple types.
"""

_required_metadata_fields = {"dependencies", "description", "name", "version"}
"""
Fields that must be present in every plug-in's metadata.
"""

_UnresolvedCandidate = collections.namedtuple("_UnresolvedCandidate", "identity metadata dependencies")
"""
Represents a candidate plug-in whose dependencies haven't yet been resolved.

We could run the __init__ of this candidate and get its metadata, but we haven't
resolved dependencies yet or registered the plug-in with its type.

This is a named tuple consisting of the following fields:
* identity: An unique identifier for the plug-in.
* metadata: The metadata of the plug-in.
* dependencies: A list of plug-in identities on which this plug-in depends.
"""

_PluginType = collections.namedtuple("_PluginType", "api register unregister validate_metadata")
"""
Represents a plug-in type plug-in.

This is a named tuple consisting of the following fields:
* api: The class that provides the API for the plug-ins of this type.
* register: The function that plug-ins of this type must register with.
* unregister: The function that plug-ins of this type get unregistered with.
* validate_metadata: The function that verifies that the metadata is valid for
	this type.
"""

class PluginError(Exception):
	"""
	Marker exception to indicate that something went wrong in the plug-in
	system.
	"""

class MetadataValidationError(PluginError):
	"""
	Marker exception to indicate that the metadata of a plug-in is invalid.
	"""

def activate(identity):
	"""
	Activates a plug-in, so that it can be used.

	The plug-in must already be discovered. The plug-in will be registered at
	all plug-in types it implements.

	:param identity: The identity of the plug-in to activate.
	"""
	if identity not in _plugins:
		api("logger").warning("Can't activate plug-in {plugin}: No such plug-in is loaded.", plugin=identity)
		return

	candidate = _plugins[identity]
	candidate_types = candidate.keys() & _plugin_types.keys() #The plug-in types to register the plug-in at.
	for candidate_type in candidate_types:
		_register(identity, candidate_type)
	else: #All registration succeeded.
		api("logger").info("Loaded plug-in {plugin}.", plugin=identity)

def add_plugin_location(location):
	"""
	Adds a location to the list of locations where the application looks for
	plug-ins.

	It looks recursively through all subfolders of the specified folder.

	:param location: The location to add to the location list.
	"""
	if not location or not os.path.isdir(location): #Invalid plug-in location.
		raise NotADirectoryError("Plug-in location is not a path: {location}".format(location=location))
	_plugin_locations.append(location)

def api(plugin_type):
	"""
	Gets the API to interact with plug-ins of the specified type.

	These APIs provide sets of functions to interact with the plug-ins of that
	type. Some API calls may invoke actions on multiple plug-ins at once, or
	just on a specific one. For details on the API of a specific plug-in type,
	please refer to the plug-in that defines the type.

	:param plugin_type: The plug-in type to get the API of.
	:return: An object with methods to interact with plug-ins of the specified
		type.
	:raises ImportError: The plug-in type is unknown.
	"""
	if plugin_type not in _plugin_types:
		raise ImportError("No API known for \"{type}\".".format(type=plugin_type))
	return _plugin_types[plugin_type].api

def discover():
	"""
	Discovers all plug-ins it can find.

	This goes through all folders of all plug-in types, and finds out what
	their metadata is. If the metadata is correct it will create a plug-in.
	When all plug-ins are loaded, the plug-ins whose dependencies can be met
	will be stored for later requesting. Along the way, if any stage in the
	progress goes wrong for a plug-in, the plug-in is discarded.

	This method can also be used to update the plug-in repository, but
	plug-ins are not deleted then. Only new plug-ins are added by this
	function.
	"""
	candidate_directories = _find_candidate_directories() #Generates a sequence of directories that might contain plug-ins.
	candidate_modules = _load_candidates(candidate_directories)
	candidates = _parse_metadata(candidate_modules)
	candidates = list(candidates) #Sync the lazy generators here because we need to have all plug-in types ready for the next stage.

	validated_candidates = _validate_metadata(candidates)
	validated_candidates = list(validated_candidates) #Sync again here because we need to know all plug-ins with their types in the next stage.
	for validated_candidate in validated_candidates:
		_plugins[validated_candidate.identity] = validated_candidate.metadata

	resolved_candidates = list(_resolve_dependencies(validated_candidates))
	for failed_candidate in [candidate for candidate in validated_candidates if candidate not in resolved_candidates]:
		deactivate(failed_candidate.identity)
	for succeeded_candidate in resolved_candidates:
		activate(succeeded_candidate.identity)

def deactivate(identity):
	"""
	Deactivates a plug-in, so that it will no longer be used.

	The plug-in will be unregistered from all plug-in types it implements.

	:param identity: The identity of the plug-in to deactivate.
	"""
	if identity not in _plugins:
		api("logger").warning("Can't deactivate plug-in {plugin}: No such plug-in is loaded.", plugin=identity)
		return

	for plugin_type in _plugins[identity]:
		if plugin_type in _required_metadata_fields: #It's a global metadata field, not a type definition.
			continue
		if plugin_type == "type": #We're deactivating a plug-in type. Do that at the very end, so we don't get errors if the plug-in implements its own type.
			continue
		if plugin_type not in _plugin_types: #The type was deleted prior, because it was a dependency.
			continue
		if identity in plugins_by_type[plugin_type]:
			_unregister(identity, plugin_type)
			api("logger").info("Unregistered plug-in {plugin} as {plugin_type}.", plugin=identity, plugin_type=plugin_type)
	if "type" in _plugins[identity]: #Now unregister any plug-in type it may define.
		del _plugin_types[_plugins[identity]["type"]["type_name"]]
		api("logger").info("Unregistered plug-in {plugin} as plug-in type.", plugin=identity)
	dependees = [dependee_identity for dependee_identity, dependee in _plugins.items() if identity in dependee["dependencies"]]
	for dependee_identity in dependees:
		deactivate(dependee_identity)

def _find_candidate_directories():
	"""
	Finds candidates for what looks like might be plug-ins.

	A candidate is a folder inside a plug-in location, which has a file
	``__init__.py``. The file is not yet executed at this point.

	:returns: A sequence of directories that supposedly contain plug-ins.
	"""
	for location in _plugin_locations:
		for root, directories, files in os.walk(location, followlinks=True):
			if "__init__.py" not in files: #The directory must have an __init__.py file.
				continue
			directories[:] = [] #Remove all subdirectories. We aren't going to look in submodules.
			yield root

def _load_candidates(directories):
	"""
	Loads plug-in candidates as Python packages.

	This is intended to be used on Python packages, containing an init
	script.

	:param directories: A sequence of paths where plug-ins can be found.
	:return: A sequence of Python packages representing plug-ins.
	"""
	for directory in directories:
		identity = os.path.basename(directory)
		parent_directory = os.path.dirname(directory)
		if "." in identity:
			try:
				api("logger").warning("Can't load plug-in {plugin}: Invalid plug-in identity; periods are forbidden.", plugin=identity)
			except ImportError: #Logger type module isn't loaded yet.
				logging.exception("Can't load plug-in {plugin}: Invalid plug-in identity; periods are forbidden.".format(plugin=identity)) #pylint: disable=logging-format-interpolation
			continue
		try:
			file, path, description = imp.find_module(identity, [parent_directory])
		except Exception as e:
			try:
				api("logger").warning("Failed to find module of plug-in in {plugin}: {error_message}", plugin=identity, error_message=str(e))
			except ImportError: #Logger type module isn't loaded yet.
				logging.exception("Failed to find module of plug-in in {plugin}: {error_message}".format(plugin=identity, error_message=str(e))) #pylint: disable=logging-format-interpolation
			continue
		try:
			module = imp.load_module(identity, file, path, description)
		except Exception as e:
			try:
				api("logger").warning("Failed to load plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
			except ImportError: #Logger type module isn't loaded yet.
				logging.exception("Failed to load plug-in {plugin}: {error_message}".format(plugin=identity, error_message=str(e))) #pylint: disable=logging-format-interpolation
			continue
		finally:
			if file: #Plug-in loading should not open any files, but if it does, close it immediately.
				try:
					api("logger").warning("Plug-in {plugin} is a file: {filename}", plugin=identity, filename=str(file))
				except ImportError: #Logger type module isn't loaded yet.
					logging.exception("Plug-in {plugin} is a file: {filename}", plugin=identity, filename=str(file)) #pylint: disable=logging-format-interpolation
				file.close()
		yield module

def _meets_requirements(candidate_metadata, requirements, candidate_identity, depending_identity):
	"""
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

def _parse_metadata(modules):
	"""
	Gets and parses the metadata of a sequence of modules.

	The metadata is then split and stored as _UnresolvedCandidate instances for
	further processing.

	:param modules: A sequence of modules to parse the metadata of.
	:return: A sequence of _UnresolvedCandidate instances representing the
	modules and metadata.
	"""
	for module in modules:
		identity = module.__name__

		try:
			metadata = module.metadata()
		except Exception as e:
			try:
				api("logger").warning("Failed to load metadata of plug-in {plugin}: {error_message}", plugin=identity, error_message=str(e))
			except ImportError: #Logger type hasn't loaded yet.
				logging.exception("Failed to load metadata of plug-in {plugin}: {error_message}".format(plugin=identity, error_message=str(e))) #pylint: disable=logging-format-interpolation
			continue

		try:
			_validate_metadata_global(metadata)
		except MetadataValidationError as e:
			try:
				api("logger").warning("Metadata of plug-in {plugin} is invalid: {error_message}", include_stack_trace=False, plugin=identity, error_message=str(e))
			except ImportError: #Logger type hasn't loaded yet.
				logging.exception("Metadata of plug-in {plugin} is invalid: {error_message}".format(plugin=identity, error_message=str(e))) #pylint: disable=logging-format-interpolation
			continue

		if "type" in metadata: #For plug-in type definitions, we have a built-in metadata checker.
			try:
				_validate_metadata_type(metadata)
			except MetadataValidationError as e:
				try:
					api("logger").warning("Metadata of type plug-in {plugin} is invalid: {error_message}", include_stack_trace=False, plugin=identity, error_message=str(e))
				except ImportError: #Logger type hasn't loaded yet.
					logging.exception("Metadata of type plug-in {plugin} is invalid: {error_message}".format(plugin=identity, error_message=str(e))) #pylint: disable=logging-format-interpolation
				continue
			register = metadata["type"]["register"] if ("register" in metadata["type"]) else lambda *args, **kwargs: None #If not present, use a no-op lambda function.
			unregister = metadata["type"]["unregister"] if ("unregister" in metadata["type"]) else lambda *args, **kwargs: None
			plugin_type = _PluginType(api=metadata["type"]["api"], register=register, unregister=unregister, validate_metadata=metadata["type"]["validate_metadata"])
			_plugin_types[metadata["type"]["type_name"]] = plugin_type
			plugins_by_type[metadata["type"]["type_name"]] = set()

		yield _UnresolvedCandidate(identity=identity, metadata=metadata, dependencies=metadata["dependencies"])

def _register(plugin_identity, type_identity):
	"""
	Registers a plug-in as a specific plug-in type.

	This registers the plug-in here in the plug-ins module, and then calls the
	register function of the plug-in type plug-in in case that plug-in wants to
	do additional work when registering a new plug-in.

	:param plugin_identity: The identity of the plug-in to register.
	:param type_identity: The plug-in type with which to register the plug-in.
	"""
	if plugin_identity in plugins_by_type[type_identity]:
		api("logger").warning("Couldn't register plug-in {plugin} as type {plugin_type} because it was already registered.", plugin=plugin_identity, plugin_type=type_identity)
		return
	plugins_by_type[type_identity].add(plugin_identity)
	try:
		_plugin_types[type_identity].register(plugin_identity, _plugins[plugin_identity])
	except Exception as e:
		api("logger").error("Couldn't register plug-in {plugin} as type {plugin_type}: {error_message}", plugin=plugin_identity, plugin_type=type_identity, error_message=str(e))
		plugins_by_type[type_identity].remove(plugin_identity)

def _resolve_dependencies(candidates):
	"""
	Makes sure that all dependencies of the candidates are met.

	This returns the candidates for which dependencies are met. Candidates for
	which the dependencies are not met are left out.

	:param candidates: The candidates to resolve the dependencies of.
	:return: A sequence of candidates which have their dependencies met.
	"""
	for candidate in candidates:
		for dependency, requirements in candidate.dependencies.items():
			for dependency_candidate in candidates:
				if dependency == dependency_candidate.identity:
					if not _meets_requirements(dependency_candidate.metadata, requirements, dependency, candidate.identity):
						dependency_met = False #Found the dependency, but it is insufficient.
						break
					else:
						dependency_met = True #Found this dependency.
						break
			else: #Dependency was not found.
				api("logger").warning("Plug-in {plugin} is missing dependency {dependency}.", plugin=candidate.identity, dependency=dependency)
				break
			if not dependency_met:
				#The _meets_requirements function does the logging then.
				break
		else: #All dependencies are resolved!
			yield candidate

def _unregister(plugin_identity, type_identity):
	"""
	Unregisters a plug-in as a specific plug-in type.

	This unregisters the plug-in here in the plug-ins module, and then calls the
	unregister function of the plug-in type plug-in in case that plug-in wants
	to do additional work when unregistering a new plug-in.

	:param plugin_identity: The identity of the plug-in to unregister.
	:param type_identity: The plug-in type from which to unregister the plug-in.
	"""
	if plugin_identity not in plugins_by_type[type_identity]:
		api("logger").warning("Couldn't unregister plug-in {plugin} as type {plugin_type} because it is not registered.", plugin=plugin_identity, plugin_type=type_identity)
		return
	plugins_by_type[type_identity].remove(plugin_identity)
	try:
		_plugin_types[type_identity].unregister(plugin_identity)
	except Exception as e:
		api("logger").error("Couldn't unregister plug-in {plugin} as type {plugin_type}: {error_message}", plugin=plugin_identity, plugin_type=type_identity, error_message=str(e))
		plugins_by_type[type_identity].add(plugin_identity)

def _validate_metadata(candidates):
	"""
	Validates the metadata of the plug-in types of a sequence of candidates.

	It validates the metadata of each plug-in type each candidate claims to
	implement.

	:param candidates: A sequence of candidates to validate.
	:return: The same sequence, but filtered to only have candidates with valid
	metadata.
	"""
	for candidate in candidates:
		candidate_types = candidate.metadata.keys() & _plugin_types.keys() #The plug-in types this candidate claims to implement.
		for candidate_type in candidate_types:
			try:
				_plugin_types[candidate_type].validate_metadata(candidate.metadata)
			except Exception as e:
				api("logger").warning("Could not validate {candidate} as a plug-in of type {type}: {error_message}", candidate=candidate.identity, type=candidate_type, error_message=str(e))
				break #Do not load this plug-in, even if other types may be valid! That could cause plug-ins to get their dependencies resolved while those dependencies don't have valid metadata.
		else: #All types got validated properly.
			yield candidate

def _validate_metadata_global(metadata):
	"""
	Checks if the global part of the metadata of a plug-in is correct.

	If it is incorrect, an exception is raised.

	The global part of the metadata includes the part of metadata that is common
	among all plug-ins.

	:param metadata: A dictionary containing the metadata of the plug-in.
	:raises MetadataValidationError: The metadata is invalid.
	"""
	allowed_requirements = {"version_max", "version_min"}
	try:
		if not _required_metadata_fields <= metadata.keys(): #Set boolean comparison: Not all required_fields in metadata.
			raise MetadataValidationError("Required fields missing: " + str(_required_metadata_fields - metadata.keys()))
		for requirements in metadata["dependencies"].values(): #Raises AttributeError if not a dictionary.
			if not requirements.keys() <= allowed_requirements:
				raise MetadataValidationError("Unknown plug-in dependency requirements {requirements}.".format(requirements=", ".join(requirements.keys() - allowed_requirements)))
	except (AttributeError, TypeError):
		raise MetadataValidationError("Metadata is not a dictionary.")

def _validate_metadata_type(metadata):
	"""
	Checks if the metadata of a plug-in type plug-in is correct.

	If it is incorrect, an exception is raised. At this point, the metadata must
	already be validated as plug-in metadata.

	:param metadata: A dictionary containing the metadata of the plug-in.
	:raises MetadataValidationError: The metadata is invalid.
	"""
	if "type" not in metadata:
		raise MetadataValidationError("This is not a plug-in type plug-in.")
	try:
		required_fields = {"type_name", "api", "validate_metadata"}
		if not required_fields <= metadata["type"].keys(): #Set boolean comparison: Not all required_fields in metadata["type"].
			raise MetadataValidationError("Required fields in type missing: " + str(required_fields - metadata["type"].keys()))
		if not callable(metadata["type"]["validate_metadata"]):
			raise MetadataValidationError("The metadata validator must be callable.")
		if metadata["type"]["validate_metadata"].__code__.co_argcount != 1:
			raise MetadataValidationError("The metadata validation function must take exactly one argument: The plug-in's metadata.")

		#Optional fields.
		if "register" in metadata["type"]: #If it is in the metadata, it must be correct.
			if not callable(metadata["type"]["register"]):
				raise MetadataValidationError("The register entry must be callable.")
			if metadata["type"]["register"].__code__.co_argcount != 2:
				raise MetadataValidationError("The register function must take exactly two arguments: The plug-in's identity and its metadata.")
		if "unregister" in metadata["type"]: #If it's in the metadata, it must be correct.
			if not callable(metadata["type"]["unregister"]):
				raise MetadataValidationError("The unregister entry must be callable.")
			if metadata["type"]["unregister"].__code__.co_argcount != 1:
				raise MetadataValidationError("The unregister function must take exactly one argument: The plug-in's identity.")
	except (AttributeError, TypeError):
		raise MetadataValidationError("The type section is not a dictionary.")