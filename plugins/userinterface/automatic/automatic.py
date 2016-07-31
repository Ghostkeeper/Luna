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
Implements the user interface plug-in interface.
"""

import luna.plugins #To get the interface we must implement and access to the logging API.

__instance = None #The instance of the currently running user interface.

class Automatic():
	"""
	A user interface that allows no control by the user.

	This user interface is designed to work without any user input. It
	automatically converts any files in the same folder it can to the output
	files using the default settings.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the Automatic user interface.
		"""
		super().__init__()

	def start(self):
		"""
		.. function:: start()
		Starts the Automatic interface.

		For now this just prints a message that the Automatic interface is
		started.
		"""
		luna.plugins.api("logger").info("Starting Automatic interface.") #Not implemented yet.

def join():
	"""
	.. function:: join()
	Blocks the current thread until the user interface has stopped.
	"""
	pass #This user interface is single-threaded, so if the start function is ran, it joins immediately.

def start():
	"""
	.. function:: start()
	Starts the user interface.

	For this automatic user interface, this runs the entire program automatically.
	"""
	__instance = Automatic()
	__instance.start()

def stop():
	"""
	.. function:: stop()
	Stops the user interface.
	"""
	pass #This user interface is single-threaded, so if the start function is ran, it stops immediately.