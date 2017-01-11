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
	#This works with a simple finite state automaton in a linear fashion:
	#initial -> integer_start -> integer -> fractional_start -> fractional -> exponent_initial -> exponent_start -> exponent
	#Each state represents what character is expected next.
	#The FSA solution is not pretty, but it's the only way it could be made to work with a possibly infinite byte stream.
	state = "initial"
	for byte in serialised:
		if state == "initial": #Initial state: May be a negative sign or integer_start.
			if byte == b"-"[0]:
				state = "integer_start"
			elif byte >= b"0"[0] and byte <= b"9"[0]:
				state = "integer"
			else:
				return False
		elif state == "integer_start": #First character of integer. An integer must have at least 1 digit.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				state = "integer"
			else:
				return False
		elif state == "integer": #Consecutive characters of the integer. May be a period, indicating start of fractional, or an E, indicating start of exponent.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				pass #Still integer.
			elif byte == b"."[0]:
				state = "fractional_start"
			elif byte == b"e"[0] or byte == b"E"[0]:
				state = "exponent_initial"
			else:
				return False
		elif state == "fractional_start": #Start of fractional part.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				state = "fractional"
			else:
				return False
		elif state == "fractional": #Continuation of factional part. May be an E, indicating start of exponent.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				pass #Still fractional part.
			elif byte == b"e"[0] or byte == b"E"[0]:
				state = "exponent_initial"
			else:
				return False
		elif state == "exponent_initial": #Initial state of exponent, may be negative or a number.
			if byte == b"-"[0] or byte == b"+"[0]:
				state = "exponent_start"
			elif byte >= b"0"[0] and byte <= b"9"[0]:
				state = "exponent"
			else:
				return False
		elif state == "exponent_start": #First character of an exponent. Not an end state.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				state = "exponent"
			else:
				return False
		elif state == "exponent": #Continuation of an exponent.
			if byte >= b"0"[0] and byte <= b"9"[0]:
				pass #Still exponent.
			else:
				return False
	return state == "fractional" or state == "exponent" #Allowable end states.

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