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
A persistent storage plug-in that writes and reads to local file storage.

These operations are done on the local hard drive.
"""

import localstorage.local_storage #The storage implementation.

def metadata():
	"""
	Provides the metadata for the local storage plug-in.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Local Storage",
		"description": "Enables reading and writing files on the local hard disk.",
		"version": 1,
		"dependencies": {
			"storagetype": {
				"version_min": 1,
				"version_max": 1
			},
		},

		"storage": {
			"can_read": localstorage.local_storage.can_read,
			"can_write": localstorage.local_storage.can_write,
			"delete": localstorage.local_storage.delete,
			"exists": localstorage.local_storage.exists,
			"move": localstorage.local_storage.move,
			"read": localstorage.local_storage.read,
			"write": localstorage.local_storage.write
		}
	}