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
	__has_win_kernel = True
except ImportError:
	windll = None
	__has_win_kernel = False
from . import buffer_info #To store the state of the console on Windows.

#Set up the default state of the Windows StdOut handle.
if __has_win_kernel: #We're on Windows Bash.
	__standard_out_handle = windll.kernel32.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
	__default_console_attributes = windll.kernel32.GetConsoleScreenBufferInfo(-11)

def critical(self, message, title="Critical"):
	"""
	.. function:: critical(message[, title])
	Logs a new critical message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message. This is ignored.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	formatted += message
	self.__colour_print(formatted, "magenta")

def debug(self, message, title="Debug"):
	"""
	.. function:: debug(message[, title])
	Logs a new debug message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message. This is ignored.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	formatted += message
	self.__colour_print(formatted, "blue")

def error(self, message, title="Error"):
	"""
	.. function:: error(message[, title])
	Logs a new error message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message. This is ignored.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	formatted += message
	self.__colour_print(formatted, "red")

def info(self, message, title="Information"):
	"""
	.. function:: info(message[, title])
	Logs a new information message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message. This is ignored.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	formatted += message
	self.__colour_print(formatted, "green")

def warning(self, message, title="Warning"):
	"""
	.. function:: warning(message[, title])
	Logs a new warning message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message. This is ignored.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	formatted += message
	self.__colour_print(formatted, "yellow")

def __colour_print(self, message, colour="default"):
	"""
	.. function:: __colour_print(message, colour)
	Prints a message with specified colour-coding.

	Since the colours need to be supported by multiple terminals, the list of
	supported colours is limited to the intersection of the colours that all the
	supported terminals support. This is the list of supported colours. The
	`colour` parameter needs to be one of these:
	* default (The default colour of the terminal).
	* red
	* yellow
	* green
	* blue
	* magenta

	:param message: The text to print.
	:param colour: The colour of the message to display. If the colour is not
	supported, the default colour is used.
	"""
	if __has_win_kernel:
		buffer_state = buffer_info.BufferInfo()
		windll.kernel32.GetConsoleScreenBufferInfo(self.__standard_out_handle, ctypes.byref(buffer_state)) #Store the old state of the output channel so we can restore it afterwards.

		if colour == "red":
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 12)
		elif colour == "yellow":
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 14)
		elif colour == "green":
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 10)
		elif colour == "blue":
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 9)
		elif colour == "magenta":
			windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, 13)
		#Else, don't set the colour (so it stays default).
		print(message)
		windll.kernel32.SetConsoleTextAttribute(self.__standard_out_handle, buffer_state.wAttributes) #Reset to old state.
	else: #Hope we have an ANSI-enabled console.
		if colour == "red":
			ansi_colour = "\033[38m"
		elif colour == "yellow":
			ansi_colour = "\033[33m"
		elif colour == "green":
			ansi_colour = "\033[32m"
		elif colour == "blue":
			ansi_colour = "\033[34m"
		elif colour == "magenta":
			ansi_colour = "\033[35m"
		else:
			ansi_colour = "" #Stay on default colour.
		print(ansi_colour + message + "\033[m") #Start code, then message, then revert to default colour.