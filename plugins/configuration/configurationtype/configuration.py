#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for storing and retrieving configuration data of the application.

This API is used by way of key-value pairs. This API behaves like a dictionary.
Every configuration type adds an entry to this dictionary with as key the
identifier of the configuration plug-in and as value a similar dictionary. This
way a hierarchical structure of configuration is produced in dictionaries. For
instance, you could get a preference like this::

	luna.plugins("configuration")["preference"]["user interface"]["language"]

You can change the value of a preference in a similar way::

	luna.plugins("configuration")["preference"]["user interface"]["language"] = "Quenya"

Adding new items to the configuration behaves differently from a normal
dictionary. A configuration item can only be created via the ``define``
function, like so::

	luna.plugins("configuration")["preference"]["user interface"].define(
		name="language"
		default="Common"
		options={"Common", "Quenya", "Sindarin"}
	)

The parameters of the ``define`` functions depend on the data type. Getting or
setting an item that doesn't exist yields a ``KeyError``

It is up to the specific configuration plug-in to decide how to store the
information persistently. It may store each unique path to a unique file on the
file system, or choose to store everything in one file. It may even choose to
store this information remotely.
"""

import collections #To implement MutableMapping, and for namedtuple.

def __getattr__(item):
	raise Exception("Not implemented yet.")

ConfigurationEntry = collections.namedtuple("ConfigurationEntry", ["value", "data_type", "validate"])
"""
An element of configuration that holds a bit more information than just the
value of the configuration item.

It needs to track a bit of metadata, too. To that end it contains the following
fields:
* ``value``: The actual value of the configuration. The "data" as it were.
* ``data_type``: The type of data contained in this entry. This needs to be the
identity of a data type plug-in.
* ``validate``: A validation predicate, which indicates whether a specific value
is allowed in this configuration entry.
"""

class Configuration(collections.MutableMapping):
	"""
	Node in the configuration tree, representing a section of configuration.

	This class wraps around a dictionary, providing access to that dictionary
	when necessary. It should behave like a normal dictionary in that respect.
	Some behaviour is restricted however:
	* Creating new entries is not allowed. Instead, the ``define`` function is
	provided that adds new entries, but requires a bit more information.
	* Setting the value of an entry is subject to restrictions. This class only
	forbids changing the value of ``configuration``-type settings. It is
	intended that the setter gets overridden though, by configuration types that
	specialise in some specific type of configuration.
	"""

	def __init__(self, *other, **initial):
		"""
		Initialises a new ``Configuration`` instance.

		The configuration is initially empty.
		"""
		self._entries = {} #Holds a ``ConfigurationEntry`` for every key.
		#Initialising with initial data is not allowed since we must enter new entries via the define function.

	def __delitem__(self, key):
		"""
		Removes an entry of configuration.
		:param key: The name of the child configuration to remove.
		"""
		del self._entries[key]

	def __getitem__(self, item):
		"""
		Gets the value of a specified child configuration.
		:param item: The name of the child configuration.
		:return: The value of the child configuration.
		"""
		return self._entries[item].value

	def __iter__(self):
		"""
		Returns an iterator that runs over the child configuration names.
		:return: An iterator over the child configuration names.
		"""
		return iter(self._entries)

	def __len__(self):
		"""
		Returns the number of child configurations.

		Further descendants are not counted, just direct children.
		:return: The number of child configurations.
		"""
		return len(self._entries)

	def __setitem__(self, key, value):
		"""
		Changes the value of the specified child configuration, if it exists.

		If the child configuration does not yet exist, this gives a
		``KeyError``, rather than adding it immediately.

		The new value is validated before setting it. If the validation fails, a
		``ValueError`` is raised.
		:param key: The key of the configuration to change.
		:param value: The new value for the configuration.
		:raises KeyError: No configuration with the specified key is found in
		this configuration.
		:raises ValueError: The specified value is not allowed in this
		configuration.
		"""
		if key not in self._entries:
			raise KeyError("{key} is not defined in this configuration.".format(key=key))
		entry = self._entries[key]
		#TODO: Add check against the data type.
		if not entry.validate(value):
			raise ValueError("A value of {value} is not allowed for setting {key}.".format(key=key, value=value))
		entry.value = value #Store the new value.

	def define(self, key, data_type, default_value, validate):
		"""
		Defines a new configuration entry.
		:param key: The key for the new configuration entry.
		:param data_type: The sort of data that will be stored in this
		configuration entry. This needs to be an identifier of a data type
		plug-in.
		:param default_value: The value that this configuration will get at
		first run.
		:param validate: A predicate function that determines whether a
		specified value is valid for this configuration entry.
		:raises KeyError: A configuration with the specified key already exists.
		"""
		if key in self._entries:
			raise KeyError("A configuration with the key {key} already exists.".format(key=key))

		#TODO: Check if the data type exists.
		#TODO: Check default value against the data type.

		if not validate(default_value):
			raise ValueError("The default value {value} for the configuration {key} is invalid according to the provided validator.".format(key=key, value=default_value))

		self._entries[key] = ConfigurationEntry(value=default_value, data_type=data_type, validate=validate)