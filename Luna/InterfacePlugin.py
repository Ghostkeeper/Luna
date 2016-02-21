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

import Luna.Plugin #Superclass.

class InterfacePlugin(Luna.Plugin.Plugin):
	"""
	Superclass for Interface-type plug-ins.

	Any plug-in that wishes to be an interface should derive from this class. It
	will ensure that the ``start()`` function exists (and that it raises a
	``NotImplementedError`` if the function is not implemented).
	"""

	APIVERSION = 1
	"""
	Version number of the Interface plug-in API.

	Each Interface plug-in carries a similar version number which determines the
	minimum API version required of Luna to allow the plug-in to function. If
	this version number is lower than the version number of the interface, the
	interface is not loaded.
	"""

	def __init__(self):
		"""
		.. function:: __init__()
		Creates a new instance of the Interface plug-in.
		"""
		super(Luna.Plugin.Plugin,self).__init__()

	def start(self):
		"""
		.. function:: start()
		Starts interfacing.

		This method should regulate the process of conversion. That is, it
		should find out where to load the input from (e.g. by asking the user),
		how to convert the input to the output (e.g. by evaluating the settings)
		and where to write the output (e.g. by reading the command line
		arguments). This is not limited to one conversion step, of course. An
		interface may keep running indefinitely until the user wants it to stop.
		"""
		raise NotImplementedError()