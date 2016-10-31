#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Validates the metadata of user interface plug-ins.
"""

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid, and logging.

def validate_metadata(metadata):
	"""
	Validates whether the specified metadata is valid for user interface
	plug-ins.

	User interface metadata must have a ``userinterface`` entry, which must
	contain three entries: ``join``, ``start`` and ``stop``. These entries must
	contain callable objects (such as functions).

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "userinterface" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a user interface plug-in.")
	required_functions = {"join", "start", "stop"}
	try:
		if not required_functions <= metadata["userinterface"].keys():
			raise luna.plugins.MetadataValidationError("The user interface specifies no functions {function_names}.".format(function_names=", ".join(required_functions - metadata["userinterface"].keys())))
		for function_name in required_functions:
			if not callable(metadata["userinterface"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The user interface metadata is not a dictionary.")