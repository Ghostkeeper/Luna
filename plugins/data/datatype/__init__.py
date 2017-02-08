#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a way to define data types.

Data types are intended to let components of the application communicate with
each other. They provide no real functionality apart from defining a way to
serialise and deserialise the data, which is required for processes to
communicate via a pipe.

Data types are identified by their plug-in identity.
"""

import re #To check whether the MIME type of plug-ins is according to specification.

import datatype.data #The API for other plug-ins to use data types with.
import luna.plugins

def metadata():
	"""
	Provides the metadata for the Data Type plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Data Type",
		"description": "Defines a type of plug-in that defines a data type, so that different components are certain they can interact with each other via this data type.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "data",
			"api": datatype.data,
			"validate_metadata": validate_metadata
		}
	}

def validate_metadata(data_metadata):
	"""
	Validates whether the specified metadata is valid for data plug-ins.

	Data metadata must have a ``deserialise``, ``is_instance``,
	``is_serialised`` and a ``serialise`` field, which must all contain callable
	objects, such as functions. The metadata may also not contain a partial
	implementation of MIME types.
	:param data_metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "data" not in data_metadata:
		raise luna.plugins.MetadataValidationError("This is not a data plug-in.")

	required_functions = {"deserialise", "is_instance", "is_serialised", "serialise"}
	try:
		if required_functions > data_metadata["data"].keys(): #All required functions must be present.
			raise luna.plugins.MetadataValidationError("The data plug-in doesn't specify the functions {function_names}.".format(function_names=required_functions - data_metadata.keys()))
		for required_function in required_functions:
			if not callable(data_metadata["data"][required_function]):
				raise luna.plugins.MetadataValidationError("The {entry} entry is not callable.".format(entry=required_function))
	except (AttributeError, TypeError):
		raise luna.plugins.MetadataValidationError("The data metadata entry is not a dictionary.")

	mimetype_entries = {"mimetype", "name"} #If one of these is present, the others must be too.
	optional_mimetype_entries = {"extensions"} #If one of these is present, the required MIME type entries must be too.
	if (mimetype_entries | optional_mimetype_entries) & data_metadata["data"].keys(): #MIME type is implemented, at least partially.
		if mimetype_entries - data_metadata["data"].keys():
			raise luna.plugins.MetadataValidationError("The data plug-in has an incomplete implementation of MIME types, missing {entries}.".format(entries=", ".join(mimetype_entries - data_metadata["data"].keys())))
		if not re.match(r"^[A-Za-z0-9][A-Za-z0-9!#\$&-\^\.\+_]{0,126}/[A-Za-z0-9][A-Za-z0-9!#\$&-\^\.\+_]{0,126}$", data_metadata["data"]["mimetype"]):
			raise luna.plugins.MetadataValidationError("The MIME type in the data plug-in is not valid according to RFC 6838: {mimetype}".format(mimetype=data_metadata["data"]["mimetype"]))
		if "extensions" in data_metadata["data"]:
			if not hasattr(data_metadata["data"]["extensions"], "__iter__"): #Must be a sequence.
				raise luna.plugins.MetadataValidationError("The extensions for the MIME type in the data plug-in are not a sequence.")
			if isinstance(data_metadata["data"]["extensions"], str): #We want to disallow strings, since iterating over them gives single characters instead of proper extensions, without giving errors at runtime.
				raise luna.plugins.MetadataValidationError("The extensions for the MIME type in the data plug-in are a single string, not a sequence.")