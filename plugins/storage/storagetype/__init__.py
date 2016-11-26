#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides functionality to save and load data to a persistent storage location.

This could be used to retain data between multiple runs of the application, such
as user preferences, or it could be used to gain additional input from an
external source, such as the file system, or save the output to a place where
other applications can access it.

The API of this plug-in type is based on "files" with a unique URI. If the
storage intended is not based on URI, a plug-in may have to emulate it and
devise a custom scheme for the URI.
"""

import luna.plugins
import storagetype.storage #The API for other plug-ins to use storage with.

def metadata():
	"""
	Provides the metadata for the StorageType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Storage Type",
		"description": "Defines a type of plug-in that stores and loads data to and from a persistent storage location.",
		"version": 3,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "storage",
			"api": storagetype.storage,
			"validate_metadata": validate_metadata
		}
	}

def validate_metadata(storage_metadata):
	"""
	Validates whether the specified metadata is valid for storage plug-ins.

	Storage metadata must have a ``storage`` entry, which must contain six
	entries: ``can_read``, ``can_write``, ``delete``, ``exists``, ``move``,
	``open_read`` and ``open_write``. These entries must contain callable
	objects (such as functions).

	:param storage_metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "storage" not in storage_metadata:
		raise luna.plugins.MetadataValidationError("This is not a storage plug-in.")
	required_functions = {"can_read", "can_write", "delete", "exists", "move", "open_read", "open_write"}
	try:
		if not required_functions <= storage_metadata["storage"].keys():
			raise luna.plugins.MetadataValidationError("The storage specifies no functions {function_names}.".format(function_names=", ".join(required_functions - storage_metadata["storage"].keys())))
		for function_name in required_functions:
			if not callable(storage_metadata["storage"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The storage metadata is not a dictionary.")