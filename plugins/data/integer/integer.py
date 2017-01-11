#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the implementation of integers as a data type definition.

Integers are serialised using the JSON format.
"""

import io #To decode UTF-8 streaming.
import json #We're using JSON to serialise integers in a readable format quickly.

import luna.plugins #To access the data API for raising SerialisationExceptions.
import luna.stream #To provide the serialised streams in their expected format.

def deserialise(serialised):
	"""
	Interprets a sequence of bytes that represents an integer.
	:param serialised: A sequence of bytes that represents an integer.
	:return: The integer that was being represented by the sequence of bytes.
	"""
	try:
		instance = json.load(io.TextIOWrapper(serialised, encoding="utf_8"))
	except UnicodeDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence is not proper UTF-8, so it doesn't represent an integer.") from e
	except JSONDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence does not represent a JSON-format document and therefore doesn't represent an integer.") from e
	if type(instance) != int:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence does not represent an integer, but an instance of type {instance_type}.".format(instance_type=type(instance)))
	return instance

def is_instance(instance):
	"""
	Detects whether some object is an integer.
	:param instance: The instance of which to check whether it is an integer.
	:return: ``True`` if the object is an integer, or ``False`` if it isn't.
	"""
	return type(instance) == int

def is_serialised(serialised):
	"""
	Detects whether a byte stream represents an integer.
	:param serialised: A byte stream which must be identified as being an
	integer or not.
	:return: ``True`` if the stream likely represents an integer, or ``False``
	if it does not.
	"""
	try:
		unicode_string = io.TextIOWrapper(serialised, encoding="utf_8").readline() #Only need at most one line.
	except UnicodeDecodeError:
		return False #If it's not UTF-8 encoded, it's not an integer.
	for character in unicode_string:
		if not character.isdigit():
			return False
	return len(unicode_string) >= 1 #All characters are digits and there is at least one digit.

def serialise(instance):
	"""
	Serialises an integer to a sequence of bytes.
	:param instance: The integer to serialise.
	:return: A sequence of bytes representing the integer.
	"""
	output = luna.stream.BytesStreamReader(io.BytesIO())
	try:
		json.dump(instance, output) #The default encoding for JSON is already UTF-8.
	except TypeError as e:
		raise luna.plugins.api("data").SerialisationException("Trying to serialise an object that is not an integer.") from e
	return output