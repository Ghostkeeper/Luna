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
An implementation of persistent storage that reads and writes from the hard
drive.

All of these operations are explicitly atomic. Multiple threads or processes
should never be working on the same data to prevent race conditions, but the
user opening multiple instances of the application can't be prevented. This
atomicity doesn't prevent race conditions in these cases, but at least prevents
data corruption.
"""

import urllib.parse #To get the scheme from a URI.

def can_read(uri):
	"""
	Determines if this plug-in could read from a URI like the one specified.

	This determination is purely made on the URI, not on the actual file system.
	It can read from the URI if the URI uses the file scheme.

	:param uri: An absolute URI.
	:return: ``True`` if this plug-in can read from the specified URI, or
		``False`` if it can't.
	"""
	return urllib.parse.urlparse(uri).scheme == "file" #Can only read from file schemes.

def can_write(uri):
	"""
	Determines if this plug-in could write to a URI like the one specified.

	This determination is purely made on the URI, not on the actual file system.
	It can write to the URI if the URI uses the file scheme.

	:param uri: An absolute URI.
	:return: ``True`` if this plug-in can write to the specified URI, or
		``False`` if it can't.
	"""
	return urllib.parse.urlparse(uri).scheme == "file" #Can only write to file schemes.

def delete(uri):
	raise RuntimeError("This functionality is not yet implemented.")

def exists(uri):
	raise RuntimeError("This functionality is not yet implemented.")

def move(source, destination):
	raise RuntimeError("This functionality is not yet implemented.")

def read(uri):
	raise RuntimeError("This functionality is not yet implemented.")

def write(uri, data):
	raise RuntimeError("This functionality is not yet implemented.")