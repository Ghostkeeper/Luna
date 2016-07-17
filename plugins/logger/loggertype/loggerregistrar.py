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

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.
import loggertype.logger #To check if a logger implements the logger interface.

__loggers = []
"""
The loggers that have been registered here so far.
"""

def get_all_loggers():
	"""
	.. function:: get_all_loggers()
	Gets all loggers that have been registered here so far.

	:return: A list of loggers.
	"""
	return __loggers

def register(metadata):
	"""
	.. function:: register(metadata)
	Registers a new logger plug-in to log with.

	This expects the metadata to already be verified as a logger's metadata.

	:param metadata: The metadata of a logger plug-in.
	"""
	__loggers.append(metadata["logger"]["implementation"]())

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
	required_fields = {"implementation"}
	try:
		if not required_fields <= metadata["logger"].keys():
			raise luna.plugins.MetadataValidationError("The logger specifies no implementation.")
		if not issubclass(metadata["logger"]["implementation"], loggertype.logger.Logger):
			raise luna.plugins.MetadataValidationError("The logger interface is not implemented.")
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The logger metadata is not a dictionary.")