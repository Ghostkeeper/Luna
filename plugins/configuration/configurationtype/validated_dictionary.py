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

import collections #For namedtuple.

import luna.plugins #To access the loggers.

class ValidatedDictionary(dict):
	"""
	A dictionary-like data structure where all values are validated.

	New keys can only be added by also providing a validator predicate. Adding
	new keys can't be done with the usual ``dictionary[key] = value``, but via a
	separate method ``add``. Adding new keys in the usual way would result in an
	exception stating that the key cannot be found.

	When setting a key to a new value, the predicate associated with the key
	will be executed to determine whether the value is allowed. If the value is
	not allowed, an exception will be raised.

	As an additional feature, items in this dictionary can be reset to their
	original value, that they were set to when they were defined. This is to
	further serve the task that this dictionary was intended for in
	configuration.

	For the rest, this class should behave like an ordinary dictionary.
	"""

	"""
	The metadata belonging to one item in the dictionary.

	This is a named tuple consisting of the following fields:
	* default: The default value for the item, meaning the original value. This
	can later be restored.
	* validator: A predicate that indicates whether a certain value is allowed
	in this item.
	"""
	_Metadata = collections.namedtuple("_Item", "default validator")

	def __init__(self):
		"""
		Initialises a new validated dictionary.

		It is initially empty.
		"""
		super().__init__()
		self._metadata = {} #The metadata for every key.

	def __setitem__(self, key, value):
		"""
		Changes the value of an item in the dictionary.

		The key must already exist at this point. If it doesn't exist, a
		``KeyError`` will be raised.

		Additionally, as per the main functionality of this class, the value is
		validated first. If the value is invalid, a ``ValueError`` will be
		raised.
		:param key: The key of the item to change.
		:param value: The new value for the item.
		:raises KeyError: The key does not exist in the dictionary.
		:raises ValueError: The value is invalid for the specified key.
		"""
		if super().__contains__(key):
			raise KeyError("The key {key} is not defined in this validated dictionary.".format(key=key))

		if not self._metadata[key].validator(value):
			raise ValueError("The value for the {key} item is invalid: {value}".format(key=key, value=str(value)))

		super().__setitem__(key, value)

	def __delitem__(self, key):
		"""
		Removes an item from the dictionary.
		:param key: The key of the item to remove.
		"""
		super().__delitem(key)
		del self._metadata[key]

	def add(self, key, value, validator = lambda _: True):
		"""
		Add a new item to the dictionary.

		If no validator is specified, all values will be considered valid for
		this key.

		The key may not exist already. If it does, a ``KeyError`` will be
		raised.
		:param key: The key of the item to add to the dictionary.
		:param value: The default value of the item to add to the dictionary.
		:param validator: A predicate that indicates whether a given value is
		valid or not. The predicate must accept exactly 1 parameter (so don't
		make it a method) and must return a value that can be cast to a boolean
		value that indicates whether the value is valid or not.
		:raises KeyError: The key already exists.
		:raises ValueError: The specified function is not a predicate.
		"""
		if super().__contains__(key):
			raise KeyError("The key {key} already exists in this validated dictionary.".format(key=key))
		if validator.__code__.co_argcount != 1: #To catch programming mistakes early, check whether this is a predicate. The method vs. function is a common mistake.
			raise ValueError("The validator for key {key} is not a predicate. It has {argument_count} arguments instead of 1.".format(key=key, argument_count = validator.__code__.co_argcount))

		super().__setitem(key, value)
		self._metadata[key] = _Metadata(default=value, validator=validator)