#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for logging messages.

This defines a number of logging levels, and allows the application to log
messages with those levels.
"""

import enum #To define the logging importance levels.
import inspect #To dissect the stack trace.
import sys #To get the stack trace.

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

_logger_levels = {}

def critical(message, title="Critical", include_stack_trace=True, **kwargs):
	"""
	Logs a new critical message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param include_stack_trace: If this function is called from within an
		exception, should a stack trace be printed?
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	stack_trace = []
	if include_stack_trace:
		traceback = sys.exc_info()[2]
		if traceback:
			stack_trace = list(reversed(inspect.getouterframes(traceback.tb_frame)[1:])) + inspect.getinnerframes(traceback)
	for logger in loggers:
		if Level.CRITICAL in _logger_levels[logger]:
			loggers[logger].critical(substituted, title, stack_trace)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def debug(message, title="Debug", include_stack_trace=True, **kwargs):
	"""
	Logs a new debug message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param include_stack_trace: If this function is called from within an
		exception, should a stack trace be printed?
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	stack_trace = []
	if include_stack_trace:
		traceback = sys.exc_info()[2]
		if traceback:
			stack_trace = list(reversed(inspect.getouterframes(traceback.tb_frame)[1:])) + inspect.getinnerframes(traceback)
	for logger in loggers:
		if Level.DEBUG in _logger_levels[logger]:
			loggers[logger].debug(substituted, title, stack_trace)
	#Since debug log messages aren't activated by default, there is no fallback for this level.
	#The fallback doesn't have this level set by default and there is no way to set it.

def error(message, title="Error", include_stack_trace=True, **kwargs):
	"""
	Logs a new error message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param include_stack_trace: If this function is called from within an
		exception, should a stack trace be printed?
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	stack_trace = []
	if include_stack_trace:
		traceback = sys.exc_info()[2]
		if traceback:
			stack_trace = list(reversed(inspect.getouterframes(traceback.tb_frame)[1:])) + inspect.getinnerframes(traceback)
	for logger in loggers:
		if Level.ERROR in _logger_levels[logger]:
			loggers[logger].error(substituted, title, stack_trace)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def info(message, title="Information", include_stack_trace=True, **kwargs):
	"""
	Logs a new information message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param include_stack_trace: If this function is called from within an
		exception, should a stack trace be printed?
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	stack_trace = []
	if include_stack_trace:
		traceback = sys.exc_info()[2]
		if traceback:
			stack_trace = list(reversed(inspect.getouterframes(traceback.tb_frame)[1:])) + inspect.getinnerframes(traceback)
	for logger in loggers:
		if Level.INFO in _logger_levels[logger]:
			loggers[logger].info(substituted, title, stack_trace)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)

def set_levels(levels, identity=None):
	"""
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
		_logger_levels[identity] = levels
	else: #If not given any specific logger name, set the log levels for all loggers.
		for logger in _logger_levels:
			_logger_levels[logger] = levels

def warning(message, title="Warning", include_stack_trace=True, **kwargs):
	"""
	Logs a new warning message with all loggers.

	:param message: The message of the log entry.
	:param title: A title for the entry.
	:param include_stack_trace: If this function is called from within an
		exception, should a stack trace be printed?
	:param kwargs: Key-word arguments. These are inserted in the message
		body. The value of a key-word argument will be put in place of the
		key surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = loggertype.loggerregistrar.get_all_loggers()
	stack_trace = []
	if include_stack_trace:
		traceback = sys.exc_info()[2]
		if traceback:
			stack_trace = list(reversed(inspect.getouterframes(traceback.tb_frame)[1:])) + inspect.getinnerframes(traceback)
	for logger in loggers:
		if Level.WARNING in _logger_levels[logger]:
			loggers[logger].warning(substituted, title, stack_trace)
	if not loggers: #There are no loggers.
		print(title + ": " + substituted)