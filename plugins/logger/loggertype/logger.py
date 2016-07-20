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
Defines an interface that logger plug-ins must implement.
"""

import abc

class Logger(metaclass=abc.ABCMeta):
	"""
	Interface that logger plug-ins must implement.

	It defines log functions for various levels of importance, and a function to
	set which of these levels should actually get added to the log.
	"""

	@abc.abstractmethod
	def critical(self, message, title="Critical"):
		"""
		.. function:: critical(message[, title])
		Logs a new critical message.

		:param message: The message text.
		:param title: A header for the message.
		"""

	@abc.abstractmethod
	def debug(self, message, title="Debug"):
		"""
		.. function:: debug(message[, title])
		Logs a new debug message.

		:param message: The message text.
		:param title: A header for the message.
		"""

	@abc.abstractmethod
	def error(self, message, title="Error"):
		"""
		.. function:: error(message[, title])
		Logs a new error message.

		:param message: The message text.
		:param title: A header for the message.
		"""

	@abc.abstractmethod
	def info(self, message, title="Info"):
		"""
		.. function:: info(message[, title])
		Logs a new information message.
		:param message:
		:param title:
		:return:
		"""

	@abc.abstractmethod
	def set_levels(self, levels):
		"""
		.. function:: set_levels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A container of log levels that will be logged.
		"""

	@abc.abstractmethod
	def warning(self, message, title="Warning"):
		"""
		.. function:: warning(message[, title])
		Logs a new warning message.

		:param message: The message text.
		:param title: A header for the message.
		"""