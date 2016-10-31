#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import luna.plugins #To log messages, and raise a MetadataValidationError if the metadata is invalid.

def validate_metadata(metadata):
	"""
	Validates whether the specified metadata is valid for configuration
	plug-ins.

	Configuration's metadata must have a ``configuration`` field, which must
	have a ``name`` entry and an ``instance`` entry. The ``instance`` entry must
	implement ``__getattr__``, ``serialise`` and ``deserialise``.

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "configuration" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a configuration plug-in.")

	try:
		if "name" not in metadata["configuration"]:
			raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify a name.")

		if "instance" not in metadata["configuration"]:
			raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify an instance to keep track of the configuration.")
	except TypeError:
		raise luna.plugins.MetadataValidationError("The configuration metadata entry is not a dictionary.")
	instance_attributes = set(dir(metadata["configuration"]["instance"]))
	required_functions = {"__getattr__", "serialise", "deserialise"}
	if required_functions > instance_attributes: #Instance is not implementing all required functions.
		raise luna.plugins.MetadataValidationError("The configuration instance doesn't implement the required functions {functions}.".format(functions=", ".join(required_functions - instance_attributes)))