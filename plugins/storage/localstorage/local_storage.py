#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An implementation of persistent storage that reads and writes from the hard
drive.

All of these operations are explicitly atomic. Multiple threads or processes
should never be working on the same data to prevent race conditions, but the
user opening multiple instances of the application can't be prevented. This
atomicity doesn't prevent race conditions in these cases, but at least prevents
data corruption.
"""

import shutil #For the move function.
import os #To delete files, get modification times and flush data to files.
import tempfile #To write to temporary files in order to write atomically.
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
	if uri is None:
		raise ValueError("Provided URI is None.")
	try:
		return urllib.parse.urlparse(uri).scheme == "file" #Can only read from file schemes.
	except ValueError: #Badly-formed IPv6 address.
		return False #We don't care. We can only read locally anyway.

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

def read(uri):
	"""
	Reads the contents of the specified file.

	This read is done atomically, meaning that it will return the state of the
	file at a single instance in time. This is achieved fairly naively by
	tracking the time of last modification in the file system, and re-trying to
	read when the time of last modification changed while the reading was in
	progress. As a result, this method is lock-free but not wait-free. It may be
	retrying indefinitely if the file keeps getting updated during the read.
	However, this algorithm is simple to implement and introduces very little
	overhead if there is nobody writing, which is the main use case.

	This algorithm is only atomic in the theoretical case of infinite time
	resolution on the last modification time stamp of the file system. This is
	obviously incorrect, but nothing better can be achieved without requiring
	all writers to the file to keep record of their precise modification count
	or something like that. On UNIX-based file systems, the time resolution is
	typically 1ns, which is more than enough. On Windows's file system, NTFS,
	the resolution is 100ns, which is often enough, except for very small files.
	On FAT, however, the time resolution is 2s, which basically obliterates the
	atomicity of this function for all but the largest files.
	This could be fixed by introducing a sleep just before the file read that is
	equal to the resolution of the time stamp, but this is deemed too costly for
	the time cost of a file read operation. It could also be improved by reading
	the file twice, and re-trying until the last two reads are equal, but that
	is also too costly, since it requires two reads for the base case where
	nothing modifies the file.

	:param uri: The URI of the resource to read.
	:return: The contents of the resource, as a bytes string.
	:raises IOError: The data could not be read.
	"""
	path = _uri_to_path(uri)

	while True:
		last_modified = os.path.getmtime(path)
		#To guarantee atomic file reads, insert a sleep here (see documentation). Disabled for speed.
		#time.sleep(0.0001) #Must be equal to the minimum resolution of the file system's last modification time stamp.
		with open(path, "rb") as file_handle: #Read in binary mode.
			result = file_handle.read()
		if os.path.getmtime(path) == last_modified: #Still not modified. We've got a good copy.
			return result

def write(uri, data):
	"""
	Writes data to a resource.

	Any old data in the resource will get overwritten. If no resource exists at
	the specified location, a new resource will be created.

	This writing is done atomically, meaning that it will appear as if the
	writing is made instantaneously. This is done by writing the data to a
	temporary file, then moving the new file on top of the old file. Therefore,
	the actual atomicity of this write depends on the atomicity of ``move``.

	:param uri: The location of the resource to write the data to.
	:param data: The data to write to the resource, as a bytes string.
	:raises IOError: The data could not be written.
	"""
	path = _uri_to_path(uri)
	directory, _ = os.path.split(path) #Put the temporary file in the same directory, so it will be on the same file system which guarantees an atomic move.
	with tempfile.NamedTemporaryFile(dir=directory, delete=False, mode="wb") as temp_handle: #Don't delete it afterwards!
		temp_handle.write(data)
		temp_handle.flush() #Make sure that it's really all written.
		os.fsync(temp_handle.fileno()) #Make sure the file system is up-to-date.
	move(temp_handle.name, uri) #Move the new file into place, replacing the old file if it existed.

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