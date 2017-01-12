#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for finding the available data types and (de)serialising them.
"""

import itertools #To split a byte sequence to check its type with every data plug-in.

import luna.plugins #To find the data types that are available.

class SerialisationException(Exception):
	"""
	Marker exception to indicate that something went wrong with serialising or
	deserialising a piece of data.
	"""
	pass

def data_types():
	"""
	Gives a set of all data types available.
	:return: A set of all data types available.
	"""
	luna.plugins.plugins_by_type["data"].keys()

def deserialise(serialised, data_type=None):
	"""
	Deserialises the specified sequence of bytes, turning it into an instance of
	the specified data type.
	:param serialised: A serialised form of data representing an instance of the
	specified data type, in the form of a byte sequence.
	:param data_type: The type of data the serialised ``bytes`` should be
	interpreted as. If no data type is provided, the data type is found
	automatically.
	:return: An instance of the specified data type.
	"""
	if data_type is None:
		data_type = type_of_serialised(serialised)
		if data_type is None:
			raise SerialisationException("The data type could not automatically be determined.")
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["data"]["deserialise"](serialised)
	except KeyError as e: #Plug-in with specified data type is not available.
		raise KeyError("There is no activated data plug-in with data type {data_type} to serialise with.".format(data_type=data_type)) from e

def is_instance(data_type, data):
	"""
	Checks whether the specified object is an instance of the specified data
	type.
	:param data_type: The data type to check for.
	:param data: An object to check the data type of.
	:return: ``True`` if the object is of the specified data type, or ``False``
	if it isn't.
	"""
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["data"]["is_instance"](data)
	except KeyError: #Plug-in with specified data type is not available.
		luna.plugins.api("logger").warning("Checking against non-existent data type {data_type}.")
		return False

def is_serialised(data_type, serialised):
	"""
	Checks whether a sequence of ``bytes`` represents an instance of the
	specified data type.
	:param data_type: The data type to check for.
	:param serialised: A sequence of bytes to check the data type of.
	:return: ``True`` if the stream of bytes represents an instance of the
	specified data type, or ``False if it doesn't.
	"""
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["data"]["is_serialised"](serialised)
	except KeyError: #Plug-in with specified data type is not available.
		luna.plugins.api("logger").warning("Checking against non-existent data type {data_type}.")
		return False

def serialise(data, data_type=None):
	"""
	Serialises the specified data.

	The result is a sequence of bytes. The ``deserialise`` operation turns it
	back into a copy of the original object.
	:param data: The data that must be serialised.
	:param data_type: The type of data that will be provided. If no data type is
	provided, the data type is found automatically.
	:return: A sequence of bytes representing exactly the state of the data.
	"""
	if data_type is None:
		data_type = type_of(data)
		if data_type is None:
			raise SerialisationException("The data type of object {instance} could not automatically be determined.".format(instance=str(data)))
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["data"]["serialise"](data)
	except KeyError as e: #Plug-in with specified data type is not available.
		raise KeyError("There is no activated data plug-in with data type {data_type} to serialise with.".format(data_type=data_type)) from e

def type_of(data):
	"""
	Attempts to find the data type of an object.

	This goes by all data types in turn and asks if any of them thinks the
	object is theirs. The first one that reports it is an instance of its data
	type will be returned, even if multiple data types would match.
	:param data: An object to find the data type of.
	:return: The data type of the object, or ``None`` if it has no known data
	type.
	"""
	for identity, data_plugin in luna.plugins.plugins_by_type["data"].items():
		if data_plugin["data"]["is_instance"](data):
			return identity
	return None #No data type found.

def type_of_serialised(serialised):
	"""
	Attempts to find the data type of a serialised form of an object.

	This goes by all data types in turn and asks if any of them thinks the bytes
	stream is theirs. The first one that reports it is a representation
	belonging to its data type is returned, even if multiple data types would
	match.
	:param serialised: A sequence of bytes to find the data type of.
	:return: The data type that the sequence represents, or ``None`` if it has
	no known data type.
	"""
	num_data_plugins = len(luna.plugins.plugins_by_type["data"])
	input_streams = itertools.tee(serialised, num_data_plugins) #Create a stream for every plug-in to read from.
	for stream, plugin in zip(input_streams, luna.plugins.plugins_by_type["data"].items()):
		identity, metadata = plugin
		if metadata["data"]["is_serialised"](stream):
			return identity
	return None #No data type found.