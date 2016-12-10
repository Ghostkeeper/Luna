#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An implementation of persistent storage that reads and writes from the hard
drive.

All of these operations are explicitly atomic. This atomicity depends on the
operating system in some part, but all of the supported operating systems
(Windows, Linux) ensure that this is possible. Not all cases of concurrent
reading and writing can be accounted for, however. In particular, if a foreign
application writes directly in the file this will not be accounted for. When
dealing only with other instances of the same application, these functions
should behave atomically.
"""

import shutil #For the move function.
import os #To delete files, get modification times and flush data to files.
import urllib.parse #To get the scheme from a URI.

import localstorage.atomic_write_stream #To implement atomic writing.

def can_read(uri):
	"""
	Determines if this plug-in could read from a URI like the one specified.

	This determination is purely made on the URI, not on the actual file system.
	It can read from the URI if the URI uses the file scheme and is not a
	directory.

	:param uri: An absolute URI.
	:return: ``True`` if this plug-in can read from the specified URI, or
	``False`` if it can't.
	"""
	if uri is None:
		raise ValueError("Provided URI is None.")
	try:
		parsed = urllib.parse.urlparse(uri)
	except ValueError: #Badly-formed IPv6 address.
		return False #We don't care. We can only read locally anyway.

	if parsed.scheme != "file": #Can only read from file names.
		return False
	if parsed.path and parsed.path[-1] != "/": #Must have a file name, not a directory.
		return False
	return True

def can_write(uri):
	"""
	Determines if this plug-in could write to a URI like the one specified.

	This determination is purely made on the URI, not on the actual file system.
	It can write to the URI if the URI uses the file scheme.

	:param uri: An absolute URI.
	:return: ``True`` if this plug-in can write to the specified URI, or
	``False`` if it can't.
	"""
	if uri is None:
		raise ValueError("Provided URI is None.")
	try:
		return urllib.parse.urlparse(uri).scheme == "file" #Can only write to file schemes.
	except ValueError: #Badly-formed IPv6 address.
		return False #We don't care. We can only write locally anyway.

def delete(uri):
	"""
	Deletes the resource at the specified location.

	:param uri: The location of the resource to delete.
	:raises IOError: The file could not be deleted.
	"""
	os.remove(_uri_to_path(uri))

def exists(uri):
	"""
	Checks if the specified resource exists.

	:param uri: The location of the resource to check for.
	:return: ``True`` if the file exists, or ``False`` if it doesn't.
	:raises IOError: The existence check could not be performed.
	"""
	return os.path.isfile(_uri_to_path(uri))

def move(source, destination):
	"""
	Moves a resource from one location to another.

	Any existing resource at the destination will get overwritten.

	:param source: The location of a resource that must be moved.
	:param destination: The new location of the resource.
	:raises IOError: Moving the resource failed.
	"""
	shutil.move(_uri_to_path(source), _uri_to_path(destination)) #Use shutil because it overwrites old files on Windows too.

def open_read(uri):
	"""
	Reads the contents of the specified file.

	This read is atomic and wait-free, as long as other Luna applications are
	the only ones that write to the file (or the applications that write are
	using the same technique to write to it). This works because the write will
	first write to a separate file and then atomically move the new file over
	the old one. All supported operating systems will keep the old file alive if
	an application is still reading it while some other file is moved on top of
	it. So if that happens, this module will still be reading from a file that
	is long gone. It reads the data that it got at the point where it opened the
	stream.

	:param uri: The URI of the resource to read.
	:return: A stream that reads the contents of the resource as a bytes string.
	:raises IOError: The file could not be opened for reading.
	"""
	path = _uri_to_path(uri)
	return open(path, "rb")

def open_write(uri):
	"""
	Opens a file for writing and returns a stream for writing to it.

	Any old data in the resource will get overwritten. If no resource exists at
	the specified location, a new resource will be created.

	This writing is done atomically, meaning that it will appear as if the
	writing is made instantaneously. This is done by writing the data to a
	temporary file, then moving the new file on top of the old file. Therefore,
	the actual atomicity of this write depends on the atomicity of ``move``.

	Since flushing the stream is directly in conflict with atomic writing,
	flushing the stream returned by this write function is not supported.

	:param uri: The location of the resource to write the data to.
	:param data: The data to write to the resource, as a bytes string.
	:raises IOError: The data could not be written.
	"""
	path = _uri_to_path(uri)
	return localstorage.atomic_write_stream.AtomicWriteStream(path)

def _uri_to_path(uri):
	"""
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