#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Validates plug-ins that register as storage.
"""

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.

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
			if not callable(metadata["storage"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The storage metadata is not a dictionary.")