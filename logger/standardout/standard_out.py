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
Implements the logger plug-in interface.
"""

import datetime #For putting timestamps alongside each message.
import ctypes #For printing in colour on Windows machines.

try:
	from ctypes import windll #For access to Windows' console API to change the colours. Needs to use the from ... import syntax for some reason.
	hasWinKernel = True
except ImportError:
	hasWinKernel = False
import luna.logger #To check against the logger levels.
import luna.logger_plugin #Superclass.
from . import buffer_info #To store the state of the console on Windows.

class StandardOut(luna.logger_plugin.LoggerPlugin):
	"""
	Logs messages to the standard output of the program.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the StandardOut logger.
		"""
		(luna.logger_plugin.LoggerPlugin, self).__init__()
		self.__levels = [luna.logger.Level.ERROR, luna.logger.Level.CRITICAL, luna.logger.Level.WARNING, luna.logger.Level.INFO] #The importance levels that are logged by default.
		self.__standardOutHandle = None
		if hasWinKernel: #Windows bash.
			self.__standardOutHandle = ctypes.windll.kernel32.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
			self.__defaultConsoleAttributes = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(-11)

	def critical(self, message, title = "Critical"):
		"""
		.. function:: critical(message[, title])
		Logs a new critical message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if luna.logger.Level.CRITICAL in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			if hasWinKernel:
				self.__colourPrintWin32(formatted, luna.logger.Level.CRITICAL)
			else:
				self.__colourPrintAnsi(formatted, luna.logger.Level.CRITICAL)

	def debug(self, message, title = "Debug"):
		"""
		.. function:: debug(message[, title])
		Logs a new debug message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if luna.logger.Level.DEBUG in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			if hasWinKernel:
				self.__colourPrintWin32(formatted, luna.logger.Level.DEBUG)
			else:
				self.__colourPrintAnsi(formatted, luna.logger.Level.DEBUG)

	def error(self, message, title = "Error"):
		"""
		.. function:: error(message[, title])
		Logs a new error message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if luna.logger.Level.ERROR in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			if hasWinKernel:
				self.__colourPrintWin32(formatted, luna.logger.Level.ERROR)
			else:
				self.__colourPrintAnsi(formatted, luna.logger.Level.ERROR)

	def info(self, message, title = "Information"):
		"""
		.. function:: info(message[, title])
		Logs a new debug message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if luna.logger.Level.INFO in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			if hasWinKernel:
				self.__colourPrintWin32(formatted, luna.logger.Level.INFO)
			else:
				self.__colourPrintAnsi(formatted, luna.logger.Level.INFO)

	def setLevels(self, levels):
		"""
		.. function:: setLevels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A list of log levels that will be logged.
		"""
		self.__levels = levels

	def warning(self, message, title = "Debug"):
		"""
		.. function:: warning(message[, title])
		Logs a new warning message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if luna.logger.Level.WARNING in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			if hasWinKernel:
				self.__colourPrintWin32(formatted, luna.logger.Level.WARNING)
			else:
				self.__colourPrintAnsi(formatted, luna.logger.Level.WARNING)

	def __colourPrintAnsi(self, message, level):
		"""
		.. function:: __colourPrintAnsi(message, level)
		Prints a message with colour-coding in ANSI-based terminals, such as the
		console of Linux.

		The colour coding is based on the level of the message:
		* Red for errors.
		* Magenta for criticals.
		* Yellow for warnings.
		* Green for information.
		* Blue for debug messages.

		:param message: The text to print.
		:param level: The warning level of the message.
		"""
		if level == luna.logger.Level.ERROR:
			ansiColour = '\033[38m' #Red.
		elif level == luna.logger.Level.CRITICAL:
			ansiColour = '\033[35m' #Magenta.
		elif level == luna.logger.Level.WARNING:
			ansiColour = '\033[33m' #Yellow.
		elif level == luna.logger.Level.INFO:
			ansiColour = '\033[32m' #Green.
		elif level == luna.logger.Level.DEBUG:
			ansiColour = '\033[34m' #Blue.
		print(ansiColour + message + '\033[m') #Start code, then message, then revert to default colour.

	def __colourPrintWin32(self, message, level):
		"""
		.. function:: __colourPrintWin32(message, level)
		Prints a message with colour-coding in Windows Bash.

		The colour coding is based on the level of the message:
		* Red for errors.
		* Magenta for criticals.
		* Yellow for warnings.
		* Green for information.
		* Blue for debug messages.

		:param message: The text to print.
		:param level: The warning level of the message.
		"""
		bufferInfo = buffer_info.BufferInfo()
		ctypes.windll.kernel32.GetConsoleScreenBufferInfo(self.__standardOutHandle, ctypes.byref(bufferInfo)) #Store the old state of the output channel.

		if level == luna.logger.Level.ERROR:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, 12) #Red.
		elif level == luna.logger.Level.CRITICAL:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, 13) #Magenta.
		elif level == luna.logger.Level.WARNING:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, 14) #Yellow.
		elif level == luna.logger.Level.INFO:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, 10) #Green.
		elif level == luna.logger.Level.DEBUG:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, 9) #Blue.
		print(message)
		ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle, bufferInfo.wAttributes) #Reset to old state.