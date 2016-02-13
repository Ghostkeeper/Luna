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
	def log(level,message,*args):
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
		print("[" + levelStr + "] " + (message % args))