#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Keeps track of all logger plug-ins.

Logger plug-ins need to register here. Their implementations are stored and may
be called upon to log something.
"""

import collections #For namedtuple.

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.

_Logger = collections.namedtuple("_Logger", "critical debug error info warning")
"""
Represents a logger plug-in.

This named tuple has one field for every function in the logger:
* critical: The function to log critical messages with.
* debug: The function to log debug messages with.
* error: The function to log error messages with.
* info: The function to log information messages with.
* warning: The function to log warning messages with.
"""

_loggers = {}
"""
The loggers that have been registered here so far, keyed by their identities.
"""

def get_all_loggers():
	"""
	Gets a dictionary of all loggers that have been registered here so far.

	The keys of the dictionary are the identities of the loggers.

	:return: A dictionary of loggers, keyed by identity.
	"""
	return _loggers

def register(identity, metadata):
	"""
	Registers a new logger plug-in to log with.

	This expects the metadata to already be verified as a logger's metadata.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of a logger plug-in.
	"""
	api = luna.plugins.api("logger") #Cache.
	if identity in _loggers:
		api.warning("Logger {logger} is already registered.", logger=identity)
		return
	api.set_levels(levels={api.Level.ERROR, api.Level.CRITICAL, api.Level.WARNING, api.Level.INFO}, identity=identity) #Set the default log levels.
	_loggers[identity] = _Logger( #Put all logger functions in a named tuple for easier access.
		critical=metadata["logger"]["critical"],
		debug=metadata["logger"]["debug"],
		error=metadata["logger"]["error"],
		info=metadata["logger"]["info"],
		warning=metadata["logger"]["warning"]
	)

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