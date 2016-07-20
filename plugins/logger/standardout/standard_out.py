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

import ctypes #For printing in colour on Windows machines.
import datetime #For putting timestamps alongside each message.
try:
	from ctypes import windll #For access to Windows' console API to change the colours. Needs to use the from ... import syntax for some reason.
	_has_win_kernel = True
except ImportError:
	windll = None
	_has_win_kernel = False
from . import buffer_info #To store the state of the console on Windows.

import luna.plugins #To get the interface we need to implement.

api = luna.plugins.api("logger") #Cache locally.

class StandardOut(luna.plugins.interface("logger")):
	"""
	Logs messages to the standard output of the program.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the StandardOut logger.
		"""
		super().__init__()
		self.__levels = [api.Level.ERROR, api.Level.CRITICAL, api.Level.WARNING, api.Level.INFO] #The importance levels that are logged by default.
		self.__standard_out_handle = None
		if _has_win_kernel: #Windows bash.
			self.__standard_out_handle = windll.kernel32.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
			self.__default_console_attributes = windll.kernel32.GetConsoleScreenBufferInfo(-11)

	def critical(self, message, title="Critical"):
		"""
		.. function:: critical(message[, title])
		Logs a new critical message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if api.Level.CRITICAL in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			self.__colour_print(formatted, api.Level.CRITICAL)

	def debug(self, message, title="Debug"):
		"""
		.. function:: debug(message[, title])
		Logs a new debug message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if api.Level.DEBUG in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			self.__colour_print(formatted, api.Level.DEBUG)

	def error(self, message, title="Error"):
		"""
		.. function:: error(message[, title])
		Logs a new error message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if api.Level.ERROR in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			self.__colour_print(formatted, api.Level.ERROR)

	def info(self, message, title="Information"):
		"""
		.. function:: info(message[, title])
		Logs a new information message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if api.Level.INFO in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			self.__colour_print(formatted, api.Level.INFO)

	def set_levels(self, levels):
		"""
		.. function:: set_levels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A list of log levels that will be logged.
		"""
		self.__levels = levels

	def warning(self, message, title="Debug"):
		"""
		.. function:: warning(message[, title])
		Logs a new warning message.

		A timestamp is added alongside the message.

		:param message: The message string.
		:param title: A header for the message. This is ignored.
		"""
		if api.Level.WARNING in self.__levels: #I'm configured to display this message.
			formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
			formatted += message
			self.__colour_print(formatted, api.Level.WARNING)

	def __colour_print(self, message, level):
		"""
		.. function:: __colour_print(message, level)
		Prints a message with appropriate colour-coding.

		The colour coding is based on the level of the message:
		* Red for errors.
		* Magenta for critical messages.
		* Yellow for warnings.
		* Green for information.
		* Blue for debug messages.

		:param message: The text to print.
		:param level: The importance level of the message.
		"""
		if _has_win_kernel:
			buffer_state = buffer_info.BufferInfo()
			windll.kernel32.GetConsoleScreenBufferInfo(self.__standard_out_handle, ctypes.byref(buffer_state)) #Store the old state of the output channel.

			if level == api.Level.ERROR:
				windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 12) #Red.
			elif level == api.Level.CRITICAL:
				windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 13) #Magenta.
			elif level == api.Level.WARNING:
				windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 14) #Yellow.
			elif level == api.Level.INFO:
				windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 10) #Green.
			elif level == api.Level.DEBUG:
				windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 9) #Blue.
			print(message)
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, buffer_state.wAttributes) #Reset to old state.
		else: #Hope we have an ANSI-enabled console.
			if level == api.Level.ERROR:
				ansi_colour = '\033[38m' #Red.
			elif level == api.Level.CRITICAL:
				ansi_colour = '\033[35m' #Magenta.
			elif level == api.Level.WARNING:
				ansi_colour = '\033[33m' #Yellow.
			elif level == api.Level.INFO:
				ansi_colour = '\033[32m' #Green.
			elif level == api.Level.DEBUG:
				ansi_colour = '\033[34m' #Blue.
			else:
				ansi_colour = '\033[m' #Default colour.
			print(ansi_colour + message + '\033[m') #Start code, then message, then revert to default colour.