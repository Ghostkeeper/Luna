#!/usr/bin/env python

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
#software, either in source code form or as a compiled binary, for any purpose,
#commercial or non-commercial, and by any means.
#
#In jurisdictions that recognize copyright laws, the author or authors of this
#software dedicate any and all copyright interest in the software to the public
#domain. We make this dedication for the benefit of the public at large and to
#the detriment of our heirs and successors. We intend this dedication to be an
#overt act of relinquishment in perpetuity of all present and future rights to
#this software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <https://unlicense.org/>

from enum import Enum #To define the log levels.
import Luna.Plugins #To call all the loggers to log.

#Enumerates the logging importance levels.
class Level(Enum):
	#For logging fatal errors that will crash the program.
	ERROR = 1

	#For logging fatal errors that will crash the current operation.
	CRITICAL = 2

	#For logging events that are probably not going the way the user intended.
	WARNING = 3

	#For logging events, at least all events that got initiated from an external
	#source.
	INFO = 4

	#Information that might be useful for a debugger to know.
	DEBUG = 5

#Provides an API to use logger plug-ins.
class Logger:
	#The default log levels to log for the fallback logger.
	__levels = [Level.ERROR,Level.CRITICAL,Level.WARNING,Level.INFO]

	#Logs a new message.
	def log(level,message,*args):
		substituted = message % args #Substitute all arguments into the message.
		loggers = Luna.Plugins.Plugins.getLoggers()
		for logger in loggers:
			logger.log(level,substituted)

		if not loggers: #If there are no loggers, fall back to the built-in logging system.
			Logger.__fallbackLog(level,substituted)

	#Sets the log levels that are logged by the loggers.
	#
	#The logger(s) will only acquire log messages with importance levels that
	#are in the list specified by the last call to this function.
	#If given a logger name, the log levels are only set for that specific
	#logger. If not given a name, the log levels are set for all loggers.
	#
	#\param levels A list of log levels that the logger(s) will log.
	#\param loggerName The identifier of a logger plug-in if setting the levels
	#for a specific logger, or None if setting the levels for all loggers.
	def setLogLevels(levels,loggerName = None):
		if loggerName: #If given a specific logger name, set the log levels only for that logger.
			plugin = Luna.Plugins.Plugins.getLogger(loggerName)
			if not plugin:
				Luna.Logger.Logger.log(Luna.Logger.Level.WARNING,"Logger %s doesn't exist.",loggerName)
				return
			plugin.setLevels(levels)
		else: #If not given any specific logger name, set the log levels for all loggers.
			for plugin in Luna.Plugins.Plugins.getLoggers():
				plugin.setLevels(levels)
			Logger.__levels = levels #Also for the fallback logger.

	#Logs a message to the standard output.
	#
	#This way of logging is meant to be kept very simple. It is used only when
	#there are no other logging methods available, still providing a way of
	#debugging if something goes wrong during the plug-in loading.
	#
	#\param level The message importance level.
	#\param message The message to log.
	def __fallbackLog(level,message):
		if level not in Logger.__levels: #I'm set not to log this.
			return
		if level == Level.ERROR:
			levelStr = "ERROR"
		elif level == Level.CRITICAL:
			levelStr = "CRITICAL"
		elif level == Level.WARNING:
			levelStr = "WARNING"
		elif level == Level.INFO:
			levelStr = "INFO"
		elif level == Level.DEBUG:
			levelStr = "DEBUG"
		print("[" + levelStr + "] " + message)