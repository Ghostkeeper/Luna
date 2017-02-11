#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a class that allows for creating global application preferences.
"""

import luna.listen #To prepare the preferences for use when plug-ins are loaded.
import luna.plugins #To get the configuration data type to extend from.

class Preferences:
	"""
	Offers a system to create global application preferences.
	"""

	def __init__(self):
		"""
		Initialises the preferences configuration instance.

		It starts off without any defined preferences.
		"""
		self._preferences = {} #The preferences, by key.

	def __contains__(self, item):
		"""
		Finds whether there is a preference with the specified key.
		:param item: The key of the preference to look for.
		:return: ``True`` if a preference with the specified key exists, or
		``False`` if there is no such key.
		"""
		return item in self._preferences

	def __getattr__(self, item):
		"""
		Gets the value of a specific preference.
		:param item: The key of the preference to get the value of.
		:return: The current value of the specified preference.
		"""
		if item.startswith("_"): #Get internal fields normally.
			return super().__getattr__(item)
		if item not in self._preferences:
			raise AttributeError("The preference {key} does not exist.".format(key=item))
		return self._preferences[item].value

	def __iter__(self):
		"""
		Returns an iterator over all preference keys.
		:return: An iterator that yields all preference keys.
		"""
		return iter(self._preferences)

	def __len__(self):
		"""
		Gives the number of preferences in existence.
		:return: The total number of preferences.
		"""
		return len(self._preferences)

	def __setattr__(self, key, value):
		"""
		Changes the value of a specific preference.
		:param key: The key of the preference to get the value of.
		:param value: The new value for the preference.
		"""
		if key.startswith("_"): #Set internal fields normally.
			return super().__setattr__(key, value)
		if key not in self._preferences:
			raise AttributeError("The preference {key} does not exist.".format(key=key))
		new_data_type = luna.plugins.api("data").type_of(value)
		if new_data_type != self._preferences[key].data_type:
			if new_data_type is None:
				raise ValueError("The type of the new value for preference {key} is unknown: {value}".format(key=key, value=str(value)))
			else:
				raise ValueError("The preference {key} may not have a value with data type {data_type}.".format(key=key, data_type=new_data_type))
		self._preferences[key].value = value

	def _define(self, identifier, name, description, default_value):
		"""
		Defines a new preference setting.

		This setting will be stored persistently and be shared across multiple
		instances of the application.
		:param identifier: A unique key for the preference by which to look it
		up.
		:param name: A human-readable name for the preference.
		:param description: A text description to help the user use the
		preference better.
		:param default_value: The default value for this preference. From this
		value the data type is also derived.
		:raises KeyError: A preference with the specified key already exists.
		"""
		if identifier in self:
			raise KeyError("A preference with the key {key} already exists.".format(key=identifier))
		if identifier.startswith("_"):
			raise KeyError("Preferences starting with an underscore are reserved, so {key} is not allowed.".format(key=identifier))
		self[identifier] = preferences.preference.Preference(name, description, default_value)

	def _metadata(self, identifier):
		"""
		Gets a dictionary of metadata of the configuration instance.

		This metadata contains a name, description and default value.
		:param identifier: The identifier of the preference to get the metadata
		of.
		:return: A dictionary of metadata on the specified preference.
		"""
		preference = self._preferences[identifier]
		return {
			"default_value": preference.default_value,
			"description": preference.description,
			"name": preference.name
		}