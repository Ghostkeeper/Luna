#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for finding the available data types and (de)serialising them.
"""

import luna.plugins #To find the data types that are available.

def data_types():
	"""
	Gives a set of all data types available.

	:return: A set of all data types available.
	"""
	luna.plugins.plugins_by_type["data"].keys()

def deserialise(data_type, serialised):
	"""
	Deserialises the specified sequence of bytes, turning it into an instance of
	the specified data type.

	:param data_type: The type of data the serialised ``bytes`` should be
	interpreted as.
	:param data: A serialised form of data representing an instance of the
	specified data type, in the form of a byte sequence.
	:return: An instance of the specified data type.
	"""
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["deserialise"](serialised)
	except KeyError: #Plug-in with specified data type is not available.
		raise KeyError("There is no activated data plug-in with data type {data_type} to serialise with.".format(data_type=data_type))

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
		return luna.plugins.plugins_by_type["data"][data_type]["is_instance"](data)
	except KeyError: #Plug-in with specified data type is not available.
		luna.plugins.api("logger").warning("Checking against non-existent data type {data_type}.")
		return False

def serialise(data_type, data):
	"""
	Serialises the specified data.

	The result is a sequence of bytes. The ``deserialise`` operation turns it
	back into a copy of the original object.

	:param data_type: The type of data that will be provided.
	:param data: The data that must be serialised.
	:return: A sequence of bytes representing exactly the state of the data.
	"""
	try:
		return luna.plugins.plugins_by_type["data"][data_type]["serialise"](data)
	except KeyError: #Plug-in with specified data type is not available.
		raise KeyError("There is no activated data plug-in with data type {data_type} to serialise with.".format(data_type=data_type))

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
		if data_plugin["is_instance"](data):
			return identity
	return None #No data type found.