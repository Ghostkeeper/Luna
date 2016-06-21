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
Provides a fallback logger plug-in that simply logs to the standard output.

There must always be a logger. The plug-ins are not 'trusted' code, so there
might not be a logger plug-in there. Therefore, a logger plug-in is defined in
Luna itself.
"""

import luna.logger #To get the log levels.
import luna.logger_plugin #To implement the plug-in.

class LoggerFallback(luna.logger_plugin.LoggerPlugin):
	"""
	A logger implementation that prints log messages to the standard output.

	This logger is a singleton.

	This class is intended to be used as logging method if there is no logger
	plug-in available. There must always be some logging.
	"""

	__instance = None
	"""
	A singleton instance for this logger.

	It wouldn't actually matter to have multiple instances of this class in the
	case of concurrency, so it's not entirely thread-safe. It's a bit overkill
	to make a new instance for every log message however.
	"""

	@classmethod
	def get_instance(cls):
		"""
		.. function:: get_instance()
		Gets a singleton fallback logger instance.

		:return: A fallback logger instance.
		"""
		if not cls.__instance:
			cls.__instance = LoggerFallback()
		return cls.__instance

	def __init__(self):
		"""
		Initialise the fallback logger, defining the log levels.
		"""
		super().__init__()

		self.__levels = [luna.logger.Level.ERROR, luna.logger.Level.CRITICAL, luna.logger.Level.WARNING, luna.logger.Level.INFO]

	def critical(self, message, title="Critical"):
		"""
		.. function:: critical(message[, title])
		Logs a critical message to the standard output.

		This way of logging is meant to be kept very simple. It is used only
		when there are no other logging methods available, still providing a way
		of debugging if something goes wrong before any loggers are loaded.

		:param message: The message to log.
		:param title: A title for the message. This is ignored.
		"""
		if luna.logger.Level.CRITICAL not in self.__levels: #I'm configured not to log this.
			return
		print("[CRITICAL]", message)

	def debug(self, message, title="Debug"):
		"""
		.. function:: debug(message[, title])
		Logs a debug message to the standard output.

		This way of logging is meant to be kept very simple. It is used only
		when there are no other logging methods available, still providing a way
		of debugging if something goes wrong before any loggers are loaded.

		:param message: The message to log.
		:param title: A title for the message. This is ignored.
		"""
		if luna.logger.Level.DEBUG not in self.__levels: #I'm configured not to log this.
			return
		print("[DEBUG]", message)

	def error(self, message, title="Error"):
		"""
		.. function:: error(message[, title])
		Logs an error message to the standard output.

		This way of logging is meant to be kept very simple. It is used only
		when there are no other logging methods available, still providing a way
		of debugging if something goes wrong before any loggers are loaded.

		:param message: The message to log.
		:param title: A title for the message. This is ignored.
		"""
		if luna.logger.Level.ERROR not in self.__levels: #I'm configured not to log this.
			return
		print("[ERROR]", message)

	def info(self, message, title="Info"):
		"""
		.. function:: info(message[, title])
		Logs an information message to the standard output.

		This way of logging is meant to be kept very simple. It is used only
		when there are no other logging methods available, still providing a way
		of debugging if something goes wrong before any loggers are loaded.

		:param message: The message to log.
		:param title: A title for the message. This is ignored.
		"""
		if luna.logger.Level.INFO not in self.__levels: #I'm configured not to log this.
			return
		print("[INFO]", message)

	def set_levels(self, levels):
		"""
		.. function:: set_levels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A list of log levels that will be logged.
		"""
		self.__levels = levels

	def warning(self, message, title="Warning"):
		"""
		.. function:: warning(message[, title])
		Logs a warning message to the standard output.

		This way of logging is meant to be kept very simple. It is used only
		when there are no other logging methods available, still providing a way
		of debugging if something goes wrong before any loggers are loaded.

		:param message: The message to log.
		:param title: A title for the message. This is ignored.
		"""
		if luna.logger.Level.WARNING not in self.__levels: #I'm configured not to log this.
			return
		print("[WARNING]", message)

	_instance = None