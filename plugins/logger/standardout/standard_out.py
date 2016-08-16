#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Implements the logger plug-in interface.
"""

import ctypes #For printing in colour on Windows machines.
import datetime #For putting timestamps alongside each message.

import standardout.buffer_info #To store the state of the console on Windows.

#Set up the default state of the Windows StdOut handle.
try:
	_win_kernel = ctypes.WinDLL("kernel32")
except AttributeError:
	_win_kernel = None
if _win_kernel: #We're on Windows Bash.
	_standard_out_handle = _win_kernel.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
	_default_console_attributes = _win_kernel.GetConsoleScreenBufferInfo(-11)
	#Test whether changing the colour actually works.
	_original_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(_original_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, 1) #Change to dark blue so we know it's not equal to the user's preferred state.
	_pre_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(_pre_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, 4) #Change to dark red.
	_post_buffer_state = standardout.buffer_info.BufferInfo()
	_win_kernel.GetConsoleScreenBufferInfo(_standard_out_handle, ctypes.byref(_post_buffer_state))
	_win_kernel.SetConsoleTextAttribute(_standard_out_handle, _original_buffer_state.wAttributes) #Change back to user's preference.
	if _pre_buffer_state.wAttributes == _post_buffer_state.wAttributes: #Didn't change.
		_win_kernel = None #We have the Windows kernel, but this terminal doesn't support changes to it. Fall back to ANSI.

def critical(message, title="Critical", stack_trace=None, exception=None):
	"""
	Logs a new critical message.

	A timestamp is added alongside the message. If a title is provided, it is
	written before the message. If a stack trace is provided, it is printed
	after the message.

	:param message: The message string.
	:param title: A header for the message.
	:param stack_trace: A trace of the call stack where the message originated,
		as a list of ``FrameInfo`` objects, most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Critical": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "magenta")
	if stack_trace:
		_print_stack_trace(stack_trace, exception)

def debug(message, title="Debug", stack_trace=None, exception=None):
	"""
	Logs a new debug message.

	A timestamp is added alongside the message. If a title is provided, it is
	written before the message. If a stack trace is provided, it is printed
	after the message.

	:param message: The message string.
	:param title: A header for the message.
	:param stack_trace: A trace of the call stack where the message originated,
		as a list of ``FrameInfo`` objects, most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Debug": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "blue")
	if stack_trace:
		_print_stack_trace(stack_trace, exception)

def error(message, title="Error", stack_trace=None, exception=None):
	"""
	Logs a new error message.

	A timestamp is added alongside the message. If a title is provided, it is
	written before the message. If a stack trace is provided, it is printed
	after the message.

	:param message: The message string.
	:param title: A header for the message.
	:param stack_trace: A trace of the call stack where the message originated,
		as a list of ``FrameInfo`` objects, most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Error": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "red")
	if stack_trace:
		_print_stack_trace(stack_trace, exception)

def info(message, title="Information", stack_trace=None, exception=None):
	"""
	Logs a new information message.

	A timestamp is added alongside the message. If a title is provided, it is
	written before the message. If a stack trace is provided, it is printed
	after the message.

	:param message: The message string.
	:param title: A header for the message.
	:param stack_trace: A trace of the call stack where the message originated,
		as a list of ``FrameInfo`` objects, most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Information": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "green")
	if stack_trace:
		_print_stack_trace(stack_trace, exception)

def warning(message, title="Warning", stack_trace=None, exception=None):
	"""
	Logs a new warning message.

	A timestamp is added alongside the message. If a title is provided, it is
	written before the message. If a stack trace is provided, it is printed
	after the message.

	:param message: The message string.
	:param title: A header for the message.
	:param stack_trace: A trace of the call stack where the message originated,
		as a list of ``FrameInfo`` objects, most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	formatted = datetime.datetime.strftime(datetime.datetime.now(), "[%H:%M:%S] ") #Format the date and time.
	if title != "Warning": #Only include the title if it is special, because the default is already indicated by the colour.
		formatted += title + ": "
	formatted += message
	_colour_print(formatted, "yellow")
	if stack_trace:
		_print_stack_trace(stack_trace, exception)

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

def _print_stack_trace(stack_trace, exception=None):
	"""
	Prints a formatted stack trace.

	The stack trace is formatted similarly to how Python formats its stack
	trace.

	:param stack_trace: A stack trace, as a list of ``FrameInfo`` objects
		resulting from ``inspect.getouterframes`` or ``inspect.getinnerframes``,
		most recent frame first.
	:param exception: An exception that was raised, if any.
	"""
	print("Stack trace:")
	for frame in stack_trace:
		print("\tFile \"{file_name}\", line {line_number}, in {function}".format(file_name=frame.filename, line_number=frame.lineno, function=frame.function))
		for line in frame.code_context:
			print("\t\t" + line.strip())
	if exception:
		print(str(exception))