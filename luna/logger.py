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
Provides an API to use logger plug-ins.
"""

from enum import Enum #To define the log levels.
import luna.logger_fallback #To get a fallback method to log on if no loggers exist.
import luna.plugins #To call all the loggers to log.

class Level(Enum):
	"""
	Enumerates the logging importance levels.
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
	logged with this level.
	"""

	DEBUG = 5
	"""
	Information that might be useful for a debugger to know.
	"""

def critical(*args, **kwargs):
	"""
	.. function:: critical(message[, title][, key=value]*)
	Logs a new critical message with all loggers.

	:param args: Positional arguments. Requires at least one argument. The first
		argument is the message of the entry. The second argument, if it exists,
		is a title for the entry. The other arguments are ignored.
	:param kwargs: Key-word arguments. These are inserted in the message body.
		The value of a key-word argument will be put in place of the key
		surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	if len(args) < 1: #Not enough arguments.
		raise TypeError("critical() missing 1 required positional argument: The message.") #More or less the same as the Python version, so people can look up the error.
	message = args[0]
	if len(args) >= 2:
		title = args[1]
	else:
		title = "CRITICAL"
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = luna.plugins.get_loggers()
	for logger in loggers:
		logger.critical(substituted, title)
	if not loggers: #There are no loggers.
		luna.logger_fallback.LoggerFallback.get_instance().critical(substituted)

def debug(*args, **kwargs):
	"""
	.. function:: debug(message[, title][, key=value]*)
	Logs a new debug message with all loggers.

	:param args: Positional arguments. Requires at least one argument. The first
		argument is the message of the entry. The second argument, if it exists,
		is a title for the entry. The other arguments are ignored.
	:param kwargs: Key-word arguments. These are inserted in the message body.
		The value of a key-word argument will be put in place of the key
		surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	if len(args) < 1: #Not enough arguments.
		raise TypeError("debug() missing 1 required positional argument: The message.") #More or less the same as the Python version, so people can look up the error.
	message = args[0]
	if len(args) >= 2:
		title = args[1]
	else:
		title = "DEBUG"
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = luna.plugins.get_loggers()
	for logger in loggers:
		logger.debug(substituted, title)
	if not loggers: #There are no loggers.
		luna.logger_fallback.LoggerFallback.get_instance().debug(substituted)

def error(*args, **kwargs):
	"""
	.. function:: error(message[, title][, key=value]*)
	Logs a new error message with all loggers.

	:param args: Positional arguments. Requires at least one argument. The first
		argument is the message of the entry. The second argument, if it exists,
		is a title for the entry. The other arguments are ignored.
	:param kwargs: Key-word arguments. These are inserted in the message body.
		The value of a key-word argument will be put in place of the key
		surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	if len(args) < 1: #Not enough arguments.
		raise TypeError("error() missing 1 required positional argument: The message.") #More or less the same as the Python version, so people can look up the error.
	message = args[0]
	if len(args) >= 2:
		title = args[1]
	else:
		title = "ERROR"
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = luna.plugins.get_loggers()
	for logger in loggers:
		logger.error(substituted, title)
	if not loggers: #There are no loggers.
		luna.logger_fallback.LoggerFallback.get_instance().error(substituted)

def info(*args, **kwargs):
	"""
	.. function:: info(message[, title][, key=value]*)
	Logs a new information message with all loggers.

	:param args: Positional arguments. Requires at least one argument. The first
		argument is the message of the entry. The second argument, if it exists,
		is a title for the entry. The other arguments are ignored.
	:param kwargs: Key-word arguments. These are inserted in the message body.
		The value of a key-word argument will be put in place of the key
		surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	if len(args) < 1: #Not enough arguments.
		raise TypeError("info() missing 1 required positional argument: The message.") #More or less the same as the Python version, so people can look up the error.
	message = args[0]
	if len(args) >= 2:
		title = args[1]
	else:
		title = "INFO"
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = luna.plugins.get_loggers()
	for logger in loggers:
		logger.info(substituted, title)
	if not loggers: #There are no loggers.
		luna.logger_fallback.LoggerFallback.get_instance().info(substituted)

def set_log_levels(levels, logger_name=None):
	"""
	.. function:: setLogLevels(levels[, loggerName])
	Sets the log levels that are logged by the loggers.

	The logger(s) will only acquire log messages with importance levels that
	are in the list specified by the last call to this function.

	If given a logger name, the log levels are only set for the specified
	logger. If not given a name, the log levels are set for all loggers.

	:param levels: A list of log levels that the logger(s) will log.
	:param logger_name: The identifier of a logger plug-in if setting the
		levels for a specific logger, or None if setting the levels for all
		loggers.
	"""
	if logger_name: #If given a specific logger name, set the log levels only for that logger.
		plugin = luna.plugins.get_logger(logger_name)
		if not plugin:
			warning("Logger {name} doesn't exist.", name=logger_name)
			return
		plugin.set_levels(levels)
	else: #If not given any specific logger name, set the log levels for all loggers.
		for plugin in luna.plugins.get_loggers():
			plugin.set_levels(levels)
		luna.logger_fallback.LoggerFallback.get_instance().set_levels(levels) #Also for the fallback logger.

def warning(*args, **kwargs):
	"""
	.. function:: warning(message[, title][, key=value]*)
	Logs a new warning message with all loggers.

	:param args: Positional arguments. Requires at least one argument. The first
		argument is the message of the entry. The second argument, if it exists,
		is a title for the entry. The other arguments are ignored.
	:param kwargs: Key-word arguments. These are inserted in the message body.
		The value of a key-word argument will be put in place of the key
		surrounded by brackets. See the Python documentation for
		``str.format`` for more details.
	"""
	if len(args) < 1: #Not enough arguments.
		raise TypeError("warning() missing 1 required positional argument: The message.") #More or less the same as the Python version, so people can look up the error.
	message = args[0]
	if len(args) >= 2:
		title = args[1]
	else:
		title = "WARNING"
	substituted = message.format(**kwargs) #Substitute all arguments into the message.
	loggers = luna.plugins.get_loggers()
	for logger in loggers:
		logger.warning(substituted, title)
	if not loggers: #There are no loggers.
		luna.logger_fallback.LoggerFallback.get_instance().warning(substituted)