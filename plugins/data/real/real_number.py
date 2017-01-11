#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the implementation of real numbers as a data type definition.

Real numbers are serialised using the JSON format for floating point numbers.
"""

import io #To decode UTF-8 streaming.
import json #We're using JSON to serialise floating point numbers in a readable format quickly.

import luna.plugins #To access the data API for raising SerialisationExceptions.
import luna.stream #To provide the serialised streams in their expected format.

def deserialise(serialised):
	"""
	Interprets a sequence of bytes that represents a real number.
	:param serialised: A sequence of bytes that represents a real number.
	:return: The real number that was being represented by the sequence of
	bytes.
	"""
	try:
		instance = json.load(io.TextIOWrapper(serialised, encoding="utf_8"))
	except UnicodeDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence is not proper UTF-8, so it doesn't represent a real number.") from e
	except json.JSONDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence does not represent a JSON-format document and therefore doesn't represent a real number.") from e
	if type(instance) != float:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence does not represent a real number, but an instance of type {instance_type}.".format(instance_type=type(instance)))
	return instance

def is_instance(instance):
	"""
	Detects whether some object is a real number.
	:param instance: The instance of which to check whether it is a real number.
	:return: ``True`` if the object is a real number, or ``False`` if it isn't.
	"""
	return type(instance) == float

def is_serialised(serialised):
	"""
	Detects whether a byte stream represents a real number.
	:param serialised: A byte stream which must be identified as being a real
	number or not.
	:return: ``True`` if the stream likely represents a real number, or
	``False`` if it does not.
	"""
	#TODO
	first_byte = True
	for byte in serialised:
		if not (byte >= b"0"[0] and byte <= b"9"[0]) and not (first_byte and byte == b"-"[0]): #Minus is allowed for first byte, as negative sign.
			return False #Not a byte representing a digit.
		first_byte = False
	return not first_byte #All characters are correct and there has been at least one byte.

def serialise(instance):
	"""
	Serialises a real number to a sequence of bytes.
	:param instance: The real number to serialise.
	:return: A sequence of bytes representing the real number.
	"""
	try:
		output = luna.stream.BytesStreamReader(json.dumps(instance).encode("utf_8"))
	except TypeError as e:
		raise luna.plugins.api("data").SerialisationException("Trying to serialise an object that is not a real number.") from e
	return output