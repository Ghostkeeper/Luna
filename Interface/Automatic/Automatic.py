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

import Luna.InterfacePlugin #Superclass.
import Luna.Logger

class Automatic(Luna.InterfacePlugin.InterfacePlugin):
	"""
	An interface that allows no control by the user.

	This interface is designed to work without any user input. It automatically
	converts any files in the same folder it can to the output files using the
	default settings.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the Automatic interface.
		"""
		super(Luna.InterfacePlugin.InterfacePlugin,self).__init__()

	def start(self):
		"""
		.. function:: start()
		Starts the Automatic interface.

		For now this just prints a message that the Automatic interface is
		started.
		"""
		Luna.Logger.Logger.log(Luna.Logger.Level.INFO,"Starting Automatic interface.") #Not implemented yet.
		return False