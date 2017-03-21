#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the implementation of integers as a data type definition.

Integers are serialised in a human-readable format as a string of base 10.
"""

import luna.plugins #To access the data API for raising SerialisationExceptions.

def deserialise(serialised):
	"""
	Interprets a sequence of bytes that represents an integer.
	:param serialised: A ``bytes`` object that represents an integer.
	:return: The integer that was being represented by the bytes.
	"""
	try:
		instance = int(serialised.decode(encoding="utf-8"))
	except UnicodeDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence is not proper UTF-8, so it doesn't represent an integer.") from e
	except ValueError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised sequence does not represent an integer with base 10.") from e
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
	Detects whether a ``bytes`` object represents an integer.
	:param serialised: A ``bytes`` instance which must be identified as being an
	integer or not.
	:return: ``True`` if the ``bytes`` likely represent an integer, or ``False``
	if they do not.
	"""
	first_byte = True
	for byte in serialised:
		if not (byte >= b"0"[0] and byte <= b"9"[0]) and not (first_byte and byte == b"-"[0]): #Minus is allowed for first byte, as negative sign.
			return False #Not a byte representing a digit.
		first_byte = False
	return not first_byte #All characters are correct and there has been at least one byte.

def serialise(instance):
	"""
	Serialises an integer to bytes.
	:param instance: The integer to serialise.
	:return: The ``bytes`` representing that integer.
	"""
	return str(instance).encode("utf_8")