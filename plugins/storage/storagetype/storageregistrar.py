#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Keeps track of all storage plug-ins.

Storage plug-ins need to register here. Their implementations are stored and may
be called upon to store or retrieve data from persistent storage.
"""

import collections #For namedtuple.

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid, and logging.

_Storage = collections.namedtuple("_Storage", "can_read can_write delete exists move read write")
"""
Represents a storage plug-in.

This named tuple has one field for every function in the storage plug-in:
* can_read: Determines if the plug-in can read from a URI.
* can_write: Determines if the plug-in can write to a URI.
* delete: Removes an entry from a URI.
* exists: Checks if a URI exists.
* move: Moves data from one URI to another.
* read: Reads from a URI.
* write: Writes to a URI.
"""

_storages = {}
"""
The storage plug-ins that have been registered here so far, keyed by their
identities.
"""

def get_all_storages():
	"""
	Gets all storage plug-ins that have been registered here so far.

	:return: A dictionary of storage plug-ins, keyed by their identities.
	"""
	return _storages

def register(identity, metadata):
	"""
	Registers a new storage plug-in to store persistent data with.

	This expects the metadata to already be verified as a storage's metadata.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of the storage plug-in.
	"""
	if identity in _storages:
		luna.plugins.api("logger").warning("Storage {storage} is already registered.", storage=identity)
		return
	_storages[identity] = _Storage( #Put all storage functions in a named tuple for easier access.
		can_read=metadata["storage"]["can_read"],
		can_write=metadata["storage"]["can_write"],
		delete=metadata["storage"]["delete"],
		exists=metadata["storage"]["exists"],
		move=metadata["storage"]["move"],
		read=metadata["storage"]["read"],
		write=metadata["storage"]["write"],
	)

def validate_metadata(metadata):
	"""
	Validates whether the specified metadata is valid for storage plug-ins.

	Storage metadata must have a ``storage`` entry, which must contain six
	entries: ``can_read``, ``can_write``, ``delete``, ``exists``, ``move``,
	``read`` and ``write``. These entries must contain callable objects (such as
	functions).

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "storage" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a storage plug-in.")
	required_functions = {"can_read", "can_write", "delete", "exists", "move", "read", "write"}
	try:
		if not required_functions <= metadata["storage"].keys():
			raise luna.plugins.MetadataValidationError("The storage specifies no functions {function_names}.".format(function_names=", ".join(required_functions - metadata["storage"].keys())))
		for function_name in required_functions:
			if not hasattr(metadata["storage"][function_name], "__call__"): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The storage metadata is not a dictionary.")