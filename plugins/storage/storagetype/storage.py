#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for storing data in a persistent storage.

This API defines ways to store data, to read data back from storage, and some
administrative tasks that acts as shortcuts for multiple tasks, such as moving
data.
"""

import os.path #To get absolute paths.
import pathlib #To get URIs from relative paths.

import luna.plugins #To use the logger API.

def delete(uri):
	"""
	Removes an entity at the specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will delete files, since the working directory has
	the file scheme.

	Any plug-in that reports it can write to the URI will be used to delete the
	entry. If there are multiple plug-ins that can write to the URI, an
	arbitrary one will be chosen.

	:param uri: The URI to delete.
	:raises IOError: The operation failed.
	"""
	uri = _to_absolute_uri(uri)
	for storage in luna.plugins.plugins_by_type["storage"].values():
		if storage["storage"]["can_write"](uri):
			try:
				return storage["storage"]["delete"](uri)
			except Exception as e:
				luna.plugins.api("logger").warning("Deleting {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with the next plug-in.
	raise IOError("No storage plug-in can delete URI: {uri}".format(uri=uri))

def exists(uri):
	"""
	Checks whether an entity exists at the specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will check for files, since the working directory has
	the file scheme.

	Any plug-in that reports it can read from the URI will be used to check for
	its existence. If there are multiple plug-ins that can read from the URI, an
	arbitrary one will be chosen.

	:param uri: The URI to check for existence.
	:return: ``True`` if the specified location exists, or ``False`` if it
		doesn't.
	:raises IOError: The operation failed.
	"""
	uri = _to_absolute_uri(uri)
	for storage in luna.plugins.plugins_by_type["storage"].values():
		if storage["storage"]["can_read"](uri):
			try:
				return storage["storage"]["exists"](uri)
			except Exception as e:
				luna.plugins.api("logger").warning("Checking existence of {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with the next plug-in.
	raise IOError("No storage plug-in can check for URI existence: {uri}".format(uri=uri))

def move(source, destination):
	"""
	Moves data from one place to another.

	Both URIs are taken relative to the application's working directory. That
	means that any relative URIs will always move files, since the working
	directory has the file scheme.

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
	source = _to_absolute_uri(source)
	destination = _to_absolute_uri(destination)
	readers = set()
	storages = luna.plugins.plugins_by_type["storage"]
	for storage in storages:
		if storages[storage]["storage"]["can_read"](source):
			readers.add(storage)
			if storages[storage]["storage"]["can_write"](destination):
				try:
					storages[storage]["storage"]["move"](source, destination) #First try a direct move with a single plug-in, it may be way more efficient.
					return #Success.
				except Exception as e:
					luna.plugins.api("logger").warning("Moving URI from {source} to {destination} failed: {error_message}", source=source, destination=destination, error_message=str(e))
					#Try with next plug-in.
	#Directly moving failed. Try reading with one plug-in, writing with another.
	for storage in storages.values():
		if storage["storage"]["can_write"](destination):
			for reader in readers:
				try:
					data = storages[reader]["storage"]["read"](source)
					break #Success.
				except Exception as e:
					luna.plugins.api("logger").warning("Reading from {source} failed: {error_message}", source=source, error_message=str(e))
					readers.remove(reader) #Don't try this one again with the next writer.
					#Try with next reader.
			else: #Got an exception each time.
				raise IOError("No storage plug-in can read from URI: {uri}".format(uri=source))
			try:
				storage["storage"]["write"](destination, data)
				return #Success.
			except Exception as e:
				luna.plugins.api("logger").warning("Writing data to {destination} failed: {error_message}", destination=destination, error_message=str(e))
				#Try with next writer.
	raise IOError("No storage plug-in can write to URI: {uri}".format(uri=destination))

def read(uri):
	"""
	Reads all data stored at a specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will read from file, since the working directory has
	the file scheme.

	Any plug-in that reports it can read from the URI will be used to read the
	data. If there are multiple plug-ins that can read from the URI, an
	arbitrary one will be chosen.

	:param uri: The URI from which to read the data.
	:return: The data stored at that URI as a ``bytes`` string.
	:raises IOError: The operation failed.
	"""
	uri = _to_absolute_uri(uri)
	for storage in luna.plugins.plugins_by_type.values():
		if storage["storage"]["can_read"](uri):
			try:
				return storage["storage"]["read"](uri)
			except Exception as e:
				luna.plugins.api("logger").critical("Reading from {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with next plug-in.
	raise IOError("No storage plug-in can read from URI: {uri}".format(uri=uri))

def write(uri, data):
	"""
	Writes data to persistent storage at a specified location.

	The URI is taken relative to the application's working directory. That means
	that any relative URIs will write to file, since the working directory has
	the	file scheme.

	Any plug-in that reports it can write to the URI will be used to write the
	data. If there are multiple plug-ins that can write to the URI, an arbitrary
	one will be chosen.

	Any old data at the specified URI will get overwritten.

	:param uri: The URI to which to write the data.
	:param data: A ``bytes`` string to write to this URI.
	:raises IOError: The operation failed.
	"""
	uri = _to_absolute_uri(uri)
	for storage in luna.plugins.plugins_by_type.values():
		if storage["storage"]["can_write"](uri):
			try:
				storage["storage"]["write"](uri, data)
				return #Success.
			except Exception as e:
				luna.plugins.api("logger").critical("Writing to {uri} failed: {error_message}", uri=uri, error_message=str(e))
				#Try with next plug-in.
	raise IOError("No storage plug-in can write to URI: {uri}".format(uri=uri))

def _to_absolute_uri(uri):
	"""
	Converts the input URI into an absolute URI, relative to the current working
	directory.

	:param uri: A URI, absolute or relative.
	:return: An absolute URI.
	"""
	if ":" in uri: #Already absolute. Is either a drive letter ("C:/") or already fully specified URI ("http://").
		return pathlib.Path(uri).as_uri() #Pathlib can take care of both these cases.
	return pathlib.Path(os.path.abspath(uri)).as_uri() #Convert to absolute path, then to URI.