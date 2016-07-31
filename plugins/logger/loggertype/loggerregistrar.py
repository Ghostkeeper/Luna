#!/usr/bin/env python

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
#software, either in source code form or as a compiled binary, for any purpose,
#commercial or non-commercial, and by any means.
#
#In jurisdictions that recognise copyright laws, the author or authors of this
#software dedicate any and all copyright interest in the software to the public
#domain. We make this dedication for the benefit of the public at large and to
#the detriment of our heirs and successors. We intend this dedication to be an
#overt act of relinquishment in perpetuity of all present and future rights to
#this software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <https://unlicense.org/>.

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
	.. function:: get_all_loggers()
	Gets a dictionary of all loggers that have been registered here so far.

	The keys of the dictionary are the identities of the loggers.

	:return: A dictionary of loggers, keyed by identity.
	"""
	return _loggers

def register(identity, metadata):
	"""
	.. function:: register(identity, metadata)
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
	.. function:: validate_metadata(metadata)
	Validates whether the specified metadata is valid for logger plug-ins.

	Logger's metadata must have a "logger" field, which contains an
	"implementation" field. This field must contain a class which inherits from
	the Logger interface.

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
			if not hasattr(metadata["logger"][function_name], "__call__"): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The logger metadata is not a dictionary.")