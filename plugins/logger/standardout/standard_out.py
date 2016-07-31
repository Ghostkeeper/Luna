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

import standardout.buffer_info #To store the state of the console on Windows.

#Set up the default state of the Windows StdOut handle.
try:
	_win_kernel = ctypes.WinDLL("kernel32")
except OSError:
	_win_kernel = None
if _win_kernel: #We're on Windows Bash.
	_standard_out_handle = _win_kernel.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
	_default_console_attributes = _win_kernel.GetConsoleScreenBufferInfo(-11)
	#Test whether changing the colour actually works.
	original_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(original_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, 1) #Change to dark blue so we know it's not equal to the user's preferred state.
	pre_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(pre_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, 4) #Change to dark red.
	post_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(post_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, original_buffer_state.wAttributes) #Change back to user's preference.
	if pre_buffer_state.wAttributes == post_buffer_state.wAttributes: #Didn't change.
		_win_kernel = None #We have the Windows kernel, but this terminal doesn't support changes to it. Fall back to ANSI.

def critical(message, title="Critical"):
	"""
	.. function:: critical(message[, title])
	Logs a new critical message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Critical": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "magenta")

def debug(message, title="Debug"):
	"""
	.. function:: debug(message[, title])
	Logs a new debug message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Debug": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "blue")

def error(message, title="Error"):
	"""
	.. function:: error(message[, title])
	Logs a new error message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Error": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "red")

def info(message, title="Information"):
	"""
	.. function:: info(message[, title])
	Logs a new information message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Information": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "green")

def warning(message, title="Warning"):
	"""
	.. function:: warning(message[, title])
	Logs a new warning message.

	A timestamp is added alongside the message.

	:param message: The message string.
	:param title: A header for the message.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Warning": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "yellow")

_win_colour_codes = {
	"red": 12,
	"yellow": 14,
	"green": 10,
	"cyan": 11,
	"blue": 9,
	"magenta": 13,
	"dark_red": 4,
	"dark_yellow": 6,
	"dark_green": 2,
	"dark_cyan": 3,
	"dark_blue": 1,
	"dark_magenta": 5,
	"black": 0,
	"dark_grey": 8,
	"light_grey": 7,
	"white": 15
}
"""
The colour codes for I/O streams in the Windows API.
"""

_ansi_colour_codes = {
	"red": "\033[38m",
	"yellow": "\033[33m",
	"green": "\033[32m",
	"cyan": "\033[36m",
	"blue": "\033[34m",
	"magenta": "\033[35m",
	"black": "\033[30m",
	"white": "\033[37m"
}
"""
The colour codes in the ANSI-specification for escape codes.
"""

def _colour_print(message, colour="default"):
	"""
	.. function:: _colour_print(message, colour)
	Prints a message with specified colour-coding.

	The colour needs to be in the ``_win_colour_codes`` dictionary as well as
	the ``_ansi_colour_codes`` dictionary in order to be supported by both
	terminals. If a colour code is provided that is not supported by a terminal,
	that message will show up in the default colour for that terminal.

	:param message: The text to print.
	:param colour: The colour of the message to display. If the colour is not
	supported, the default colour is used.
	"""
	if _win_kernel:
		buffer_state = standardout.buffer_info.BufferInfo()
		_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(buffer_state)) #Store the old state of the output channel so we can restore it afterwards.

		if colour in _win_colour_codes:
			_win_kernel.SetConsoleTextAttribute(_standard_out_handle, _win_colour_codes[colour]) #Set the colour of the terminal to the desired colour.
		#Else, don't set the colour (so it stays default).
		print(message)
		_win_kernel.SetConsoleTextAttribute(_standard_out_handle, buffer_state.wAttributes) #Reset to old state.
	else: #Hope we have an ANSI-enabled console.
		if colour in _ansi_colour_codes:
			print(_ansi_colour_codes[colour] + message + "\033[m") #Start code, then message, then revert to default colour.
		else:
			print(message) #Stay on default colour.