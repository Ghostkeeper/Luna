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
Provides functionality to save and load data to a persistent storage location.

This could be used to retain data between multiple runs of the application, such
as user preferences, or it could be used to gain additional input from an
external source, such as the file system, or save the output to a place where
other applications can access it.

The API of this plug-in type is based on "files" with a unique URI. If the
storage intended is not based on URI, a plug-in may have to emulate it and
devise a custom schema for the URI.
"""

import storagetype.storage #The API for other plug-ins to use storage with.
import storagetype.storageregistrar #Where storage plug-ins must register.

def metadata():
	"""
	.. function:: metadata()
	Provides the metadata for the StorageType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Storage Type",
		"description": "Defines a type of plug-in that stores and loads data to and from a persistent storage location.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "storage",
			"api": storagetype.storage,
			"register": storagetype.storageregistrar.register,
			"validate_metadata": storagetype.storageregistrar.validate_metadata
		}
	}