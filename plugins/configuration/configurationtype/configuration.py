#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for storing and retrieving configuration data of the application.

This API is used by retrieving the configuration types as attributes of this
API. These attributes contain configuration instances, which behave in the same
way. For instance, imagine a configuration type called "preferences". These
preferences contain a preference category called "user_interface", which then
contain a preference called "language". That preference would then be accessed
like this::

	luna.plugins("configuration").preferences.user_interface.language

You can change the value of a preference in a similar way::

	luna.plugins("configuration").preferences.user_interface.language = "Quenya"

Adding new items to the configuration behaves differently, since new entries may
require additional metadata. A configuration item can only be created via the
``define`` method, like so::

	luna.plugins("configuration").preferences.user_interface.define(
		key="language"
		default="Common"
		validate=lambda language_key: language_key in luna.plugins("internationalisation").languages
	)

This would define a preference called "language". It specifies the default
value, from which the data type is also inferred. And it specifies a validation
function, which checks that a value must be one of the supported languages.

Getting or setting a configuration item that doesn't exist yields an
``AttributeError``.
"""

import sys #To replace the module with an instance of configuration in order to allow directly calling the API as if it were a configuration instance.

import luna.plugins #To call the data type API.

class Configuration:
	"""
	The root node of the configuration tree.

	This basic implementation allows only other configuration entries to be
	defined. Furthermore, changing the values of settings after defining them is
	disabled due to the nature of its contents, being configuration types.

	This class is implemented by referring to the currently active plug-ins,
	rather than keeping any actual data. This prevents data duplication. For
	this reason and the reasons listed above, this implementation is not a good
	example to use as a reference on how to implement new configuration types.
	Refer to actual configuration type implementations for an example.
	"""

	def __contains__(self, item):
		"""
		Returns whether the specified configuration type exists.
		:param item: The identifier of the configuration type to check for.
		:return: ``True`` if a configuration type exists with the specified
		identifier, or ``False`` if no such type exists.
		"""
		return item in luna.plugins.plugins_by_type["configuration"]

	def __getattr__(self, attribute):
		"""
		Gets the specified configuration type by its identifier.
		:param attribute: The name of the configuration type.
		:return: The configuration instance of the specified configuration type.
		:raises AttributeError: No configuration type with the specified name
		exists.
		"""
		try:
			return luna.plugins.plugins_by_type["configuration"][attribute]["instance"]
		except KeyError as e:
			raise AttributeError("No configuration type {attribute} exists.".format(attribute=attribute)) from e

	def __iter__(self):
		"""
		Returns an iterator that runs over all configuration type names.
		:return: An iterator over the child configuration names.
		"""
		return iter(luna.plugins.plugins_by_type["configuration"])

	def __len__(self):
		"""
		Returns the number of configuration types.
		:return: The number of configuration types.
		"""
		return len(luna.plugins.plugins_by_type["configuration"])

	def __setattr__(self, attribute, value):
		"""
		This action is disallowed. It raises an exception.

		Normally this would change the configuration instance of a configuration
		type. Since this configuration instance should always be the
		configuration instance that the configuration type provides, it may not
		be changed.
		:param attribute: The configuration type to change.
		:param value: The new configuration instance for the type.
		:raises AttributeError: Always raised, because changing configuration
		instances is not allowed.
		"""
		raise AttributeError("Changing the configuration instances of configuration types directly is not allowed.")

	def define(self, identifier):
		"""
		This action is disallowed. It raises an exception.

		Normally this would add a configuration type to the base of the
		configuration tree, but since this configuration tree is maintained by
		the plug-in structure, configuration types can only be added by
		registering a plug-in to do so.
		:param identifier: The identifier of the configuration entry you would
		want to add.
		:raise NotImplementedError: Always raised, because adding configuration
		types is not allowed.
		"""
		raise NotImplementedError("Defining new configuration types directly is not allowed.")

	def load(self, directory):
		raise NotImplementedError("Not implemented yet.")

	def metadata(self, identifier): #pylint: disable=no-self-use
		"""
		Gets a dictionary of metadata for the specified configuration type.

		Configuration types have no metadata, so this dictionary is empty.
		:param identifier: The configuration type to get the metadata of.
		:return: An empty dictionary.
		:raise KeyError: The specified configuration type doesn't exist.
		"""
		if identifier not in luna.plugins.plugins_by_type["configuration"]: #While we always give an empty dictionary, we should only give it for configuration types that exist.
			raise KeyError("The configuration type {identifier} doesn't exist.".format(identifier=identifier))
		return {}

	def save(self, directory):
		raise NotImplementedError("Not implemented yet.")

sys.modules[__name__] = Configuration()