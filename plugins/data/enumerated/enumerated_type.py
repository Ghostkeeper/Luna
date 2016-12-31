#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the implementation of enumerated types as a data type definition.
"""

import enum #To check types against the Enum class.
import pickle #To serialise Enums.

def serialise(instance):
	"""
	Serialises an enumerated type.

	:param instance: The instance of an enumerated type.
	:return: A byte sequence representing the enumerated type.
	"""
	return pickle.dumps(instance, protocol=pickle.HIGHEST_PROTOCOL) #Only need to be compatible with this same version of Python, so always use the highest protocol.

def deserialise(serialised):
	"""
	Deserialises a serialisation of an enumerated type.

	:param serialised: A sequence of bytes that represents an enumerated type.
	:return: An instance of the enumerated type the sequence represents.
	"""
	return pickle.loads(serialised)

def is_instance(instance):
	"""
	Detects whether an object is an instance of an enumerated type.

	:param instance: The object to determine the type of.
	:return: ``True`` if the instance is an enumerated type, or ``False`` if
	it's not.
	"""
	return isinstance(instance, enum.Enum)

def is_serialised(serialised):
	"""
	Detects whether a byte sequence represents an enumerated type.

	:param serialised: A sequence of bytes of which the represented type is
	unknown.
	:return: ``True`` if the sequence represents an enumerated type, or
	``False`` if it doesn't.
	"""
	raise NotImplementedError("The is_serialised function is not yet implemented.")