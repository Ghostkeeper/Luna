#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a way to configure the application to the user's liking, and store this
configuration persistently for the user.

The plug-in registers an API that allows storing of user configuration and later
reading that configuration back.
"""

import configurationtype.configuration #The API for other plug-ins to use configuration with.
import luna.plugins

def metadata():
	"""
	Provides the metadata for the ConfigurationType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Configuration Type",
		"description": "Defines a type of plug-in that stores a configuration for the application persistently.",
		"version": 1,
		"dependencies": {
			"datatype": {
				"version_min": 1,
				"version_max": 1
			}
		},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "configuration",
			"api": configurationtype.configuration,
			"validate_metadata": validate_metadata
		}
	}

def validate_metadata(configuration_metadata):
	"""
	Validates whether the specified metadata is valid for configuration
	plug-ins.

	Configuration's metadata must have a ``configuration`` field, which must
	have a ``name`` entry and an ``instance`` entry. The ``instance`` entry must
	implement ``__getitem__``, ``__iter__``, ``serialise`` and ``deserialise``.
	:param configuration_metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "configuration" not in configuration_metadata:
		raise luna.plugins.MetadataValidationError("This is not a configuration plug-in.")

	try:
		if "name" not in configuration_metadata["configuration"]:
			raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify a name.")

		if "instance" not in configuration_metadata["configuration"]:
			raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify an instance to keep track of the configuration.")
	except TypeError:
		raise luna.plugins.MetadataValidationError("The configuration metadata entry is not a dictionary.")
	instance_attributes = set(dir(configuration_metadata["configuration"]["instance"]))
	required_methods = {"__getattr__", "__iter__", "__setattr__", "define", "metadata"}
	if required_methods > instance_attributes: #Instance is not implementing all required functions.
		raise luna.plugins.MetadataValidationError("The configuration instance doesn't implement the required functions {functions}.".format(functions=", ".join(required_methods - instance_attributes)))