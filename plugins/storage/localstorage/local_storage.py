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

import os #To delete files and get modification times.
import urllib.parse #To get the scheme from a URI.

def can_read(uri):
	"""
	.. function:: can_read(uri)
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
	.. function:: can_write(uri)
	Determines if this plug-in could write to a URI like the one specified.

	This determination is purely made on the URI, not on the actual file system.
	It can write to the URI if the URI uses the file scheme.

	:param uri: An absolute URI.
	:return: ``True`` if this plug-in can write to the specified URI, or
		``False`` if it can't.
	"""
	return urllib.parse.urlparse(uri).scheme == "file" #Can only write to file schemes.

def delete(uri):
	"""
	.. function:: delete(uri)
	Deletes the resource at the specified location.

	:param uri: The location of the resource to delete.
	:raises IOError: The file could not be deleted.
	"""
	os.remove(_uri_to_path(uri))

def exists(uri):
	raise RuntimeError("This functionality is not yet implemented.")

def move(source, destination):
	raise RuntimeError("This functionality is not yet implemented.")

def read(uri):
	"""
	.. function read(uri):
	Reads the contents of the specified file.

	This read is done atomically, meaning that it will return the state of the
	file at a single instance in time. This is achieved fairly naively by
	tracking the time of last modification in the file system, and re-trying to
	read when the time of last modification changed while the reading was in
	progress. As a result, this method is lock-free but not wait-free. It may be
	retrying indefinitely if the file keeps getting updated during the read.
	However, this algorithm is simple to implement and introduces very little
	overhead if there is nobody writing, which is the main use case.

	:param uri: The URI of the file to read.
	:return: The contents of the file, as a bytes string.
	"""
	path = _uri_to_path(uri)

	while True:
		last_modified = os.path.getmtime(path)
		with open(path, "rb") as file_handle: #Read in binary mode.
			result = file_handle.read()
		if os.path.getmtime(path) == last_modified: #Still not modified. We've got a good copy.
			return result

def write(uri, data):
	raise RuntimeError("This functionality is not yet implemented.")

def _uri_to_path(uri):
	"""
	.. function _uri_to_path(uri)
	Converts a URI to a local path that can be read by Python's file I/O.

	This already assumes that this is local. The input must have been checked by
	``can_read`` or ``can_write``.

	:param uri: The URI to convert to a path.
	:return: A local path that can be read by Python's file I/O.
	"""
	parsed = urllib.parse.urlparse(uri)
	if parsed.netloc: #Network location on Windows (Unix uses normal paths like /mnt/... or /media/...).
		return "//" + parsed.netloc + parsed.path
	else: #Local file.
		if ":" in parsed.path: #All paths are absolute. Only the Windows local paths have a drive letter in them.
			return parsed.path[1:] #URI has an additional slash before it to indicate that it's absolute, but Python I/O can't take that.
		else: #Unix path.
			return parsed.path