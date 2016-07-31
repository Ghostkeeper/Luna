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
An API for logging messages.

This defines a number of logging levels, and allows the application to log
messages with those levels.
"""

import enum #To define the logging importance levels.

import loggertype.loggerregistrar #To get the logger plug-ins to log with.

class Level(enum.Enum):
	"""
	Enumerates the logging severity levels.
	"""

	ERROR = 1
	"""
	For logging fatal errors that will crash the program.
	"""

	CRITICAL = 2
	"""
	For logging fatal errors that will crash the current operation.
	"""

	WARNING = 3
	"""
	For logging events that are probably not going the way the user intended.
	"""

	INFO = 4
	"""
	For logging events.

	At least all events that got initiated from an external source must be
	logged with this level, such as user input.
	"""

	DEBUG = 5
	"""
	Information that might be useful for a debugger to know.
	"""

__logger_levels = {}

def critical(message, title="Critical", **kwargs):
	"""
	.. function:: critical(message[, title][, key=value]*)
	Logs a new critical message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	for logger in loggers:
		if Level.CRITICAL in __logger_levels[logger]:
			loggers[logger].critical(substituted, title)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def debug(message, title="Debug", **kwargs):
	"""
	.. function:: debug(message[, title][, key=value]*)
	Logs a new debug message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	for logger in loggers:
		if Level.DEBUG in __logger_levels[logger]:
			loggers[logger].debug(substituted, title)
	#Since debug log messages aren't activated by default, there is no fallback for this level.
	#The fallback doesn't have this level set by default and there is no way to set it.

def error(message, title="Error", **kwargs):
	"""
	.. function:: error(message[, title][, key=value]*)
	Logs a new error message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	for logger in loggers:
		if Level.ERROR in __logger_levels[logger]:
			loggers[logger].error(substituted, title)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def info(message, title="Information", **kwargs):
	"""
	.. function:: info(message[, title][, key=value]*)
	Logs a new information message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	for logger in loggers:
		if Level.INFO in __logger_levels[logger]:
			loggers[logger].info(substituted, title)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def set_levels(levels, identity=None):
	"""
	.. function:: set_levels(levels[, identity])
	Sets the log levels that are logged by the loggers.

	The logger(s) will only acquire log messages with severity levels that are
	in the list specified by the last call to this function.

	If given a logger identity, the log levels are only set for the specified
	logger. If not given a name, the log levels are set for all loggers.

	:param levels: A list of log levels that the logger(s) will log.
	:param identity: The identity of a logger plug-in if setting the levels for
		a specific logger, or None if setting the levels for all loggers.
	"""
	if identity: #If given a specific logger identity, set the log levels only for that logger.
		__logger_levels[identity] = levels
	else: #If not given any specific logger name, set the log levels for all loggers.
		for logger in __logger_levels:
			__logger_levels[logger] = levels

def warning(message, title="Warning", **kwargs):
	"""
	.. function:: warning(message[, title][, key=value]*)
	Logs a new warning message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	for logger in loggers:
		if Level.WARNING in __logger_levels[logger]:
			loggers[logger].warning(substituted, title)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)