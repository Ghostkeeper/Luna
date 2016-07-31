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
Provides the concept of user interfaces.

This allows for the creation of plug-ins that provide user interfaces. These do
not necessarily need to be graphical user interfaces. A user interface is simply
a routine that will show something to the user and possibly allow the user to
communicate to the application.

The plug-in registers an API to launch the user interface with, and to allow
"""

import userinterfacetype.userinterface #The API for other plug-ins to use the user interface with.
import userinterfacetype.userinterfaceregistrar #Where user interface plug-ins must register.

def metadata():
	"""
	.. function:: metadata()
	Provides metadata for the UserInterfaceType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:return: Dictionary of metadata.
	"""
	return {
		"name": "User Interface Type",
		"description": "Defines a type of plug-in that communicates with the user by showing information to the user and allowing the user to control the application.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "userinterface",
			"api": userinterfacetype.userinterface,
			"register": userinterfacetype.userinterfaceregistrar.register,
			"validate_metadata": userinterfacetype.userinterfaceregistrar.validate_metadata
		}
	}