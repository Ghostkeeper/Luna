#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the implementation of enumerated types as a data type definition.
"""

import enum #To check types against the Enum class.
import io #To decode streams of UTF-8 data lazily.
import sys #To find pre-loaded enums in their original modules.
import unicodedata #To see if the serialisation of enums has only allowed characters.

import luna.plugins #To raise a SerialisationException.

def serialise(instance):
	"""
	Serialises an enumerated type.
	:param instance: The instance of an enumerated type.
	:return: A byte sequence representing the enumerated type.
	:raises SerialisationException: The serialisation does not represent an
	enumerated type.
	"""
	try:
		reference = instance.__module__ + "." + instance.__class__.__qualname__ + "." + instance.name
	except AttributeError: #Translate the cryptic type error that arises from this if it is no enum.
		raise luna.plugins.api("data").SerialisationException("Trying to serialise something that is not an enumerated type: {instance}".format(instance=str(instance)))
	return reference.encode(encoding="utf_8")

def deserialise(serialised):
	"""
	Deserialises a serialisation of an enumerated type.
	:param serialised: A sequence of bytes that represents an enumerated type.
	:return: An instance of the enumerated type the sequence represents.
	:raises SerialisationException: The serialisation does not represent an
	enumerated type.
	"""
	try:
		serialised_string = serialised.read().decode(encoding="utf_8")
	except UnicodeDecodeError as e:
		raise luna.plugins.api("data").SerialisationException("The serialised data is not UTF-8 encoded.") from e
	path_segments = serialised_string.split(".")
	if path_segments[0] not in sys.modules:
		raise luna.plugins.api("data").SerialisationException("The serialised data does not represent an enumerated type or is not imported: {serialised}".format(serialised=serialised_string))
	enum_instance = sys.modules[path_segments[0]]
	for path_segment in path_segments[1:]: #Continue iterating where we left off.
		try:
			enum_instance = getattr(enum_instance, path_segment) #Walk down the path with getattr.
		except AttributeError as e:
			raise luna.plugins.api("data").SerialisationException("The serialised data requests an enumerated type {qualname} that doesn't exist.".format(qualname=serialised_string)) from e
	return enum_instance

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
	try:
		unicode_string = io.TextIOWrapper(serialised, encoding="utf_8").readline() #Only need at most one line.
	except UnicodeDecodeError:
		return False #If it's not UTF-8 encoded, it's not an enum.
	next_should_continue = False #Whether the next character should be a continuation character (True) or a start character (False)
	for character in unicode_string:
		if next_should_continue: #Should be a continuation character.
			if not _is_id_continue(character) and character != ".": #Also allow periods since Enums are serialised as fully qualified names.
				return False
			if character == ".":
				next_should_continue = False
		else: #Should be a start character.
			if not _is_id_start(character):
				return False
			next_should_continue = True
	return next_should_continue #All characters are correct, but we mustn't end with an empty piece.

_allowed_id_continue_categories = {"Ll", "Lm", "Lo", "Lt", "Lu", "Mc", "Mn", "Nd", "Nl", "Pc"}
"""
Character categories that Python identifiers are allowed to continue with.
"""

_allowed_id_continue_characters = {"_", "\u00B7", "\u0387", "\u1369", "\u136A", "\u136B", "\u136C", "\u136D", "\u136E", "\u136F", "\u1370", "\u1371", "\u19DA", "\u2118", "\u212E", "\u309B", "\u309C"}
"""
Additional characters that Python identifiers are allowed to continue with.
"""

_allowed_id_start_categories = {"Ll", "Lm", "Lo", "Lt", "Lu", "Nl"}
"""
Character categories that Python identifiers are allowed to start with.
"""

_allowed_id_start_characters = {"_", "\u2118", "\u212E", "\u309B", "\u309C"}
"""
Additional characters that Python identifiers are allowed to start with.
"""

def _is_id_start(character):
	"""
	Returns whether a character is an allowed first character of an identifier
	in Python.
	:param character: The character to check for.
	:return: ``True`` if the character is allowed as a first character, or
	``False`` if it isn't.
	"""
	return unicodedata.category(character) in _allowed_id_start_categories or character in _allowed_id_start_categories or unicodedata.category(unicodedata.normalize("NFKC", character)) in _allowed_id_start_categories or unicodedata.normalize("NFKC", character) in _allowed_id_start_characters

def _is_id_continue(character):
	"""
	Returns whether a character is an allowed continuation character of an
	identifier in Python.
	:param character: The character to check for.
	:return: ``True`` if the character is allowed as a first character, or
	``False`` if it isn't.
	"""
	return unicodedata.category(character) in _allowed_id_continue_categories or character in _allowed_id_continue_characters or unicodedata.category(unicodedata.normalize("NFKC", character)) in _allowed_id_continue_categories or unicodedata.normalize("NFKC", character) in _allowed_id_continue_characters