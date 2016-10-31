#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Keeps track of all logger plug-ins.

Logger plug-ins need to register here. Their implementations are stored and may
be called upon to log something.
"""

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.

def register(identity, metadata):
	"""
	Sets the log levels of a new plug-in to the defaults.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of a logger plug-in.
	"""
	api = luna.plugins.api("logger") #Cache.
	api.set_levels(levels={api.Level.ERROR, api.Level.CRITICAL, api.Level.WARNING, api.Level.INFO}, identity=identity) #Set the default log levels.

def validate_metadata(metadata):
	"""
	Validates whether the specified metadata is valid for logger plug-ins.

	Logger's metadata must have a ``logger`` field, which must contain five
	entries: ``critical``, ``debug``, ``error``, ``info`` and ``warning``. These
	entries must contain callable objects (such as functions).

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "logger" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a logger plug-in.")
	required_functions = {"critical", "debug", "error", "info", "warning"}
	try:
		if not required_functions <= metadata["logger"].keys(): #All functions must be present.
			raise luna.plugins.MetadataValidationError("The logger specifies no functions {function_names}.".format(function_names=", ".join(required_functions - metadata["logger"].keys())))
		for function_name in required_functions:
			if not callable(metadata["logger"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The logger metadata is not a dictionary.")