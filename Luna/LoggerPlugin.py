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
Provides an interface for logger plug-ins.
"""

import Luna.Logger #To access the log levels.
import Luna.Plugin #Superclass.

class LoggerPlugin(Luna.Plugin.Plugin):
	"""
	Superclass for Logger-type plug-ins.

	Any plug-in that wishes to be a logger should derive from this class. It
	will ensure that the logging functions exist (and that it raises a
	``NotImplementedError`` if the function is not implemented).
	"""

	APIVERSION = 4
	"""
	Version number of the Logger plug-in API.

	Each Logger plug-in carries a similar version number which determines the
	minimum API version required of Luna to allow the plug-in to function. If
	this version number is lower than the version number of the logger, the
	logger is not loaded.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the Logger plug-in.
		"""
		super(Luna.Plugin.Plugin,self).__init__()

	def critical(self,message,title = "Critical"):
		"""
		.. function:: critical(message[,title])
		Adds a new critical message to the log.

		:param message: The message to log.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def debug(self,message,title = "Debug"):
		"""
		.. function:: debug(message[,title])
		Adds a new debug message to the log.

		:param message: The message to log.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def error(self,message,title = "Error"):
		"""
		.. function:: error(message[,title])
		Adds a new error message to the log.

		:param message: The message to log.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def info(self,message,title = "Info"):
		"""
		.. function:: info(message[,title])
		Adds a new information message to the log.

		:param message: The message to log.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def setLevels(self,levels):
		"""
		.. function:: setLevels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A list of log levels that will be logged.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def warning(self,message,title = "Warning"):
		"""
		.. function:: warning(message[,title])
		Adds a new warning message to the log.

		:param message: The message to log.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.