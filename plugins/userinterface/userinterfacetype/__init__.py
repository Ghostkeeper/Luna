#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the concept of user interfaces.

This allows for the creation of plug-ins that provide user interfaces. These do
not necessarily need to be graphical user interfaces. A user interface is simply
a routine that will show something to the user and possibly allow the user to
communicate to the application.

The plug-in registers an API to launch the user interface with, and to allow
"""

import luna.plugins
import userinterfacetype.user_interface #The API for other plug-ins to use the user interface with.

def metadata():
	"""
	Provides metadata for the UserInterfaceType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:return: Dictionary of metadata.
	"""
	return {
		"name": "User Interface Type",
		"description": "Defines a type of plug-in that communicates with the user by showing information to the user and allowing the user to control the application.",
		"version": 2,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "userinterface",
			"api": userinterfacetype.user_interface,
			"validate_metadata": validate_metadata
		}
	}

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