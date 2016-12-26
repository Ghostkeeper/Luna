#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Registers MIME types for files that can be opened with the application.

The MIME types are collected by the build system to allow the user to register
the MIME types to be opened with the application. This plug-in type has no real
API, but only ensures that the implementers of a MIME type provide the ``read``
and ``can_read`` functions and the necessary metadata for the installer.
"""

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.
import mimetype.mime #The API for MIME plug-ins.

def metadata():
	"""
	Provides the metadata for the MIMEType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "MIME Type",
		"description": "Defines a type of plug-in that registers MIME types for files that the application is able to open.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "mime",
			"api": mimetype.mime,
			"validate_metadata": validate_metadata
		}
	}

def validate_metadata(mime_metadata):
	"""
	Validates that the specified metadata is valid for MIME plug-ins.

	MIME plug-ins' metadata must have a ``mime`` field, which must contain two
	callables: ``can_read`` and ``read``. It must also provide the MIME type
	itself as a string, a human-readable name for the type, and optionally a
	list of extensions.

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	try:
		if "mime" not in mime_metadata:
			raise luna.plugins.MetadataValidationError("This is not a MIME plug-in.")
		required_functions = {"can_read", "read"}
		if not required_functions <= mime_metadata["mime"].keys(): #All functions must be present.
			raise luna.plugins.MetadataValidationError("The MIME specifies no functions {function_names}.".format(function_names=", ".join(required_functions - mime_metadata["mime"].keys())))
		for function_name in required_functions:
			if not callable(mime_metadata["mime"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
		if "mimetype" not in mime_metadata["mime"]:
			raise luna.plugins.MetadataValidationError("The MIME type is missing from the MIME's metadata.")
		if "name" not in mime_metadata["mime"]:
			raise luna.plugins.MetadataValidationError("The human-readable name is missing from the MIME's metadata.")
		if "extensions" in mime_metadata["mime"]: #If there are extensions, it must be a sequence.
			if not hasattr(mime_metadata["mime"]["extensions"], "__iter__"):
				raise luna.plugins.MetadataValidationError("The extensions for the MIME type are not a sequence.")
			if isinstance(mime_metadata["mime"]["extensions"], str): #We want to disallow strings, since iterating over them gives single characters instead of proper extensions, without giving errors at runtime.
				raise luna.plugins.MetadataValidationError("The extensions for the MIME type are a single string, not a sequence.")
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The MIME metadata is not a dictionary.")