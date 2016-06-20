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
A plug-in that provides an interface which runs completely automatically.

The purpose of this interface is to require no user interaction at all. It just
handles the process all on its own, without fuss. This makes it easy to just run
Luna very quickly in a folder with some files that have to be converted.
"""

import automatic.automatic as automatic_module #Prevent mixing up the package name and the module name!
import luna.interface_plugin
import luna.logger_plugin

def metadata():
	"""
	.. function:: metadata()
	Provides the metadata for the Automatic plug-in.

	:returns: Dictionary of metadata.
	"""
	return {
		"apiVersions": {
			luna.interface_plugin.InterfacePlugin: (2, 2),
			luna.logger_plugin.LoggerPlugin:       (4, 4)
		},
		"type": "interface",
		"class": automatic_module.Automatic,
		"dependencies": [
			"Logger/StandardOut"
		]
	}