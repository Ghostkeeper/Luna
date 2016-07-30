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
Provides logging functionality, to allow creating plug-ins that log messages.
How those messages are stored or displayed may vary between loggers.

The plug-in registers an API to call upon the loggers to log messages as well as
an interface for logger plug-ins to implement.
"""

import loggertype.log #The API for other plug-ins to use loggers with.
import loggertype.loggerregistrar #Where logger plug-ins must register.

def metadata():
	"""
	.. function:: metadata()
	Provides the metadata for the LoggerType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Logger Type",
		"description": "Defines a type of plug-in that keeps a log of messages, intended to show what's happening behind the scenes of the application.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "logger",
			"api": loggertype.log,
			"register": loggertype.loggerregistrar.register,
			"validate_metadata": loggertype.loggerregistrar.validate_metadata
		}
	}