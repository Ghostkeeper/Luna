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

import Luna.Logger #To access the log levels.
import Luna.Plugin #Superclass.

class LoggerPlugin(Luna.Plugin.Plugin):
	"""
	Superclass for Logger-type plug-ins.

	Any plug-in that wishes to be a logger should derive from this class. It
	will ensure that the ``log()`` function exists (and that it raises a
	``NotImplementedError`` if the function is not implemented).
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the Logger plug-in.
		"""
		super(Luna.Plugin.Plugin,self).__init__()

	def log(self,level,message,title = ""):
		"""
		.. function:: log(level,message[,title])
		Adds a new log entry.

		Depending on the method of logging, not all parameters of this function
		have to be used. For instance, a text-only logger may choose to omit the
		title of the message in the log.

		:param level: The importance level of logging.
		:param message: The body of information of this log entry. All
			information regarding the log entry should be contained in this
			except the level.
		:param title: A header for the log entry.
		"""
		raise NotImplementedError() #A subclass must implement this.

	def setLevels(self,levels):
		"""
		.. function:: setLevels(levels)
		Changes which log levels are logged.

		After this function is called, the log should only acquire messages with
		a log level that is in the list of levels passed to this function.

		:param levels: A list of log levels that will be logged.
		"""
		raise NotImplementedError() #A subclass must implement this.