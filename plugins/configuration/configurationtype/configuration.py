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

import configparser #To store and read configuration items without MIME types in a config file.
import io #Converting config files quickly from and to bytes.
import os #To get environment variables to find the configuration directory.
import os.path #To join paths to construct the configuration directory.
import platform #To detect the current platform, for finding the configuration directory.
import sys #To replace the module with an instance of configuration in order to allow directly calling the API as if it were a configuration instance.

import luna #To get the application name.
import luna.plugins #To call the data type API and to log things.

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

	def save(self):
		"""
		Saves all configuration to persistent storage.

		Configuration items which have their own MIME type, such as the
		configuration type itself, will get stored in a separate file in a
		folder named after their parent configuration. Configuration items that
		don't have a MIME type will get stored inside their parent configuration
		item. This way, the configuration is stored in a manner that is both
		logical to humans reading the file structure and extensible for all
		sorts of configuration types.
		"""
		directory = self._configuration_directory()
		self._save_configuration(self, "configuration", directory) #Entry point of recursive saving.

	def _configuration_directory(self):
		"""
		Gets the directory where to save all configuration.
		:return: A URI pointing to a directory to save the configuration.
		"""
		system = platform.system()
		if system == "Windows":
			local_dir = os.getenv("LOCALAPPDATA")
			if not local_dir: #Environment variable wasn't defined.
				local_dir = os.path.expanduser("~\\AppData\\Local\\")
			return os.path.join(local_dir, luna.application_name)
		elif system == "Linux":
			config_dir = os.getenv("XDG_CONFIG_HOME")
			if not config_dir: #Environment variable wasn't defined.
				config_dir = os.path.expanduser("~/.config")
			return os.path.join(config_dir, luna.application_name)
		elif system == "Darwin":
			support_dir = os.path.expanduser("~/Library/Application Support")
			return os.path.join(support_dir, luna.application_name)
		else: #Unknown system!
			luna.plugins.api("logger").warning("Unknown system: {system}. I don't know where to save my configuration!", system=system)
			return os.path.join(os.getcwd(), luna.application_name)

	def _save_configuration(self, configuration, name, directory):
		"""
		Saves a configuration instance to a specified directory.

		The configuration items in this configuration are split into three
		parts:
		* The configuration items that don't have a MIME type will get saved in
		a .cfg file, in a key-value pair format. If there are no items without
		MIME type, the file is not created.
		* The configuration items that do have a MIME type will get saved in
		their own files in a subdirectory made for their parent configuration
		(this instance).
		* Configuration items that are of the configuration type themselves will
		get saved recursively into a subdirectory made for their parent
		configuration (this instance). This may create one directory and one
		configuration file in the subdirectory, but name clashes are impossible
		because they both get the same identifier, but one gets an extension.

		The aforementioned second and third part may cause a directory to appear
		with the same name as this configuration item's identifier. If there are
		no items in the second or third category, no directory is created.

		This creates the following sort of structure, for example:
		-                      (configuration.cfg is empty and therefore left out.)
		-configuration         (Directory created for MIME-typed items in configuration.)
		  |-                   (preferences.cfg is empty and therefore left out.)
		  |- preferences       (Directory created for MIME-typed items in preferences.)
		  |   |- general.cfg   (general has items with MIME type as well as without, so there is a subdirectory and a file with the name.)
		  |   |- general       (Directory created for MIME-typed items in general.)
		  |   |   |- macro1.py (Item that has a MIME type.)
		  |   |   |- macro2.py (Item that has a MIME type.)
		  |   |- tools.cfg     (tools has items without MIME type so there is a file for those.)
		  |   |-               (tools has no items with MIME type so there is no subdirectory.)
		:param configuration: The configuration instance to save.
		:param name: The name of the configuration instance.
		:param directory: The directory to save it in.
		"""
		#Save all child configuration items without a MIME type to a config file.
		serialised = self._serialise(self)
		filename = name
		extensions = luna.plugins.api("data").extensions("configuration")
		if extensions:
			filename += "." + next(iter(extensions)) #Take the first known extension.
		luna.plugins.api("storage").write(os.path.join(directory, filename), serialised)

		#Save all child configurations with a MIME type in separate files.
		subdirectory = os.path.join(directory, name)
		for item in configuration:
			data_type = configuration.metadata(item)["data_type"]
			if data_type == "configurationtype": #If it's a sub-configuration, call recursively so that subdirectory gets filled.
				self._save_configuration(configuration[item], item, subdirectory)
			elif luna.plugins.api("data").mime_type(data_type): #The item has a MIME type. Save it as a separate file.
				serialised = luna.plugins.api("data").serialise(configuration[item], data_type)
				self._ensure_directory(subdirectory)
				filename = item
				extensions = luna.plugins.api("data").extensions(data_type)
				if extensions:
					filename += "." + next(iter(extensions)) #Take the first known extension.
				luna.plugins.api("storage").write(os.path.join(subdirectory, filename), serialised)

	@staticmethod
	def _serialise(configuration):
		"""
		Serialises a configuration instance so that it can be stored in a file.

		All configuration items that don't have a MIME type are stored in the
		file, since the configuration items that do have a MIME type should get
		stored in separate files.

		The configuration items are stored in the config format, which is just
		key=value pairs.
		:param configuration: The configuration instance to serialise.
		:return: The ``bytes`` that represent the configuration instance.
		"""
		parser = configparser.ConfigParser()
		parser.add_section("values")
		for child_identifier in configuration: #Fill a parser with the serialised versions of all children.
			metadata = configuration.metadata(child_identifier)
			child_serialised = luna.plugins.api("data").serialise(configuration[child_identifier], data_type=metadata["data_type"])
			parser["values"][child_identifier] = child_serialised.decode("latin_1") #Latin-1 is a single-byte character set, which is bijective and never gives decoding errors.
		#Would've been nice to have a configparser that could directly write to bytes and handle bytes input as well.
		result_stream = io.BytesIO()
		parser.write(result_stream)
		result_stream.seek(0) #Rewind so that we can return all contents.
		return result_stream.read()

sys.modules[__name__] = Configuration()