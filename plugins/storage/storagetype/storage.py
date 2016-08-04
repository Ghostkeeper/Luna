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
An API for storing data in a persistent storage.

This API defines ways to store data, to read data back from storage, and some
administrative tasks that acts as shortcuts for multiple tasks, such as moving
data.
"""

import os.path #To get absolute paths.

import luna.plugins #To use the logger API.
import storagetype.storageregistrar #To get the logger plug-ins to log with.

def delete(uri):
	"""
	.. function:: delete(uri)
	Removes an entity at the specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will delete files, since the working directory has
	the file schema.

	Any plug-in that reports it can write to the URI will be used to delete the
	entry. If there are multiple plug-ins that can write to the URI, an
	arbitrary one will be chosen.

	:param uri: The URI to delete.
	:raises IOError: The operation failed.
	"""
	uri = os.path.abspath(uri)
	for storage in storagetype.storageregistrar.get_all_storages().values():
		if storage.can_write(uri):
			try:
				return storage.delete(uri)
			except Exception as e:
				luna.plugins.api("logger").warning("Deleting {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with the next plug-in.
	raise IOError("No storage plug-in can delete URI: {uri}".format(uri=uri))

def exists(uri):
	"""
	.. function:: exists(uri)
	Checks whether an entity exists at the specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will check for files, since the working directory has
	the file schema.

	Any plug-in that reports it can read from the URI will be used to check for
	its existence. If there are multiple plug-ins that can read from the URI, an
	arbitrary one will be chosen.

	:param uri: The URI to check for existence.
	:return: ``True`` if the specified location exists, or ``False`` if it
		doesn't.
	:raises IOError: The operation failed.
	"""
	uri = os.path.abspath(uri)
	for storage in storagetype.storageregistrar.get_all_storages().values():
		if storage.can_read(uri):
			try:
				return storage.exists(uri)
			except Exception as e:
				luna.plugins.api("logger").warning("Checking existence of {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with the next plug-in.
	raise IOError("No storage plug-in can check for URI existence: {uri}".format(uri=uri))

def move(source, destination):
	"""
	.. function:: move(source, destination)
	Moves data from one place to another.

	Both URIs are taken relative to the application's working directory. That
	means that any relative URIs will always move files, since the working
	directory has the file schema.

	Any plug-in that reports it can read from the source and write to the
	destination will be used to move the data. If there are multiple plug-ins
	that can do both, an arbitrary one will be chosen. If there are none that
	can do both, a plug-in will be chosen to read the data from the source, and
	a different plug-in will be chosen to write the data to the destination.

	Any old data at the destination will get overwritten.

	:param source: The URI of the data to move.
	:param destination: The new URI of the data.
	:raises IOError: The operation failed.
	"""
	source = os.path.abspath(source)
	destination = os.path.abspath(destination)
	readers = set()
	storages = storagetype.storageregistrar.get_all_storages()
	for storage in storages:
		if storages[storage].can_read(source):
			readers.add(storage)
			if storages[storage].can_write(destination):
				try:
					storages[storage].move(source, destination) #First try a direct move with a single plug-in, it may be way more efficient.
					return #Success.
				except Exception as e:
					luna.plugins.api("logger").warning("Moving URI from {source} to {destination} failed: {error_message}", source=source, destination=destination, error_message=str(e))
					#Try with next plug-in.
	#Directly moving failed. Try reading with one plug-in, writing with another.
	for storage in storages.values():
		if storage.can_write(destination):
			for reader in readers:
				try:
					data = storages[reader].read(source)
					break #Success.
				except Exception as e:
					luna.plugins.api("logger").warning("Reading from {source} failed: {error_message}", source=source, error_message=str(e))
					readers.remove(reader) #Don't try this one again with the next writer.
					#Try with next reader.
			else: #Got an exception each time.
				raise IOError("No storage plug-in can read from URI: {uri}".format(uri=source))
			try:
				storage.write(destination, data)
				return #Success.
			except Exception as e:
				luna.plugins.api("logger").warning("Writing data to {destination} failed: {error_message}", destination=destination, error_message=str(e))
				#Try with next writer.
	raise IOError("No storage plug-in can write to URI: {uri}".format(uri=destination))

def read(uri):
	"""
	.. function:: read(uri)
	Reads all data stored at a specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will read from file, since the working directory has
	the file schema.

	Any plug-in that reports it can read from the URI will be used to read the
	data. If there are multiple plug-ins that can read from the URI, an
	arbitrary one will be chosen.

	:param uri: The URI from which to read the data.
	:return: The data stored at that URI as a ``bytes`` string.
	:raises IOError: The operation failed.
	"""
	uri = os.path.abspath(uri)
	for storage in storagetype.storageregistrar.get_all_storages().values():
		if storage.can_read(uri):
			try:
				return storage.read(uri)
			except Exception as e:
				luna.plugins.api("logger").critical("Reading from {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with next plug-in.
	raise IOError("No storage plug-in can read from URI: {uri}".format(uri=uri))

def write(uri, data):
	"""
	.. function:: write(uri, data)
	Writes data to persistent storage at a specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will write to file, since the working directory has
	the	file schema.

	Any plug-in that reports it can write to the URI will be used to write the
	data. If there are multiple plug-ins that can write to the URI, an arbitrary
	one will be chosen.

	Any old data at the specified URI will get overwritten.

	:param uri: The URI to which to write the data.
	:param data: A ``bytes`` string to write to this URI.
	:raises IOError: The operation failed.
	"""
	uri = os.path.abspath(uri)
	for storage in storagetype.storageregistrar.get_all_storages().values():
		if storage.can_write(uri):
			try:
				storage.write(uri, data)
				return #Success.
			except Exception as e:
				luna.plugins.api("logger").critical("Writing to {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with next plug-in.
	raise IOError("No storage plug-in can write to URI: {uri}".format(uri=uri))