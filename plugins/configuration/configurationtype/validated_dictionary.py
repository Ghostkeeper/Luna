#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a dictionary-like data structure where all values are validated.

The purpose of this dictionary is to be used in configuration data structures
where the keys are more or less frozen after the application has completed its
start-up phase.
"""

class ValidatedDictionary:
	"""
	A dictionary-like data structure where all values are validated.

	New keys can only be added by also providing a validator predicate. Adding
	new keys can't be done with the usual ``dictionary[key] = value``, but via a
	separate method ``add``. Adding new keys in the usual way would result in an
	exception stating that the key cannot be found.

	When setting a key to a new value, the predicate associated with the key
	will be executed to determine whether the value is allowed. If the value is
	not allowed, an exception will be raised.

	For the rest, this class should behave like an ordinary dictionary.
	"""
	pass #Not yet implemented.