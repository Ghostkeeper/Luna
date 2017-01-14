.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

===================================
Implementing configuration plug-ins
===================================
This document gives instructions on how to implement a configuration plug-in. A configuration plug-in stores some part of the user's configuration. This will then be stored on the hard disk and retained between runs of the application. Other components of the application can read and store information in the configuration.

A configuration plug-in stores a set of configuration items. Each configuration item has an identifier, but for the rest may consist of any object. The API provides a blind filter that filters configuration items in a particular configuration plug-in by the attributes on the objects.

To implement a configuration plug-in, one needs to provide a name for the configuration by which the type of configuration can be identified, and an object that provides the functionality to store configuration. The object needs to provide a way to access individual elements of configuration, iterate over them, and has methods to serialise and deserialise its content.

---------------------
Filtering on metadata
---------------------
The configuration API provides a way to filter configuration based on metadata. This is implemented via the iteration over the elements of the plug-ins. The filtering looks for attributes of the objects that are returned by the iteration. The objects returned by the iteration are not specified by this API though. It is assumed that the caller of the filter depends on the particular configuration plug-in and version, and therefore knows the attributes it can filter on. There is no way in which a configuration plug-in needs to expose which fields are available in an item.

Each configuration item is expected to have the same attributes. It is advisable to make them instances of the same class.

------------------
Configuration name
------------------
The configuration name is a name by which the API exposes the type of configuration externally. Since it is exposed via attribute access on the API, the name needs to adhere to the `syntax of a Python identifier`_.

.. _syntax of a Python identifier: https://docs.python.org/3/reference/lexical_analysis.html#identifiers

----------------------
Configuration instance
----------------------
The configuration instance is an instance of the class that basically implements the configuration type you provide. The instance must provide the following methods.

----

	.. function:: __getitem__(self, item)

Gets a configuration item with a specified identifier.

- ``item``: The identifier of the item to get.
- Return: The configuration item with the specified identifier.
- Raises: ``KeyError`` if no item with the specified identifier exists in this configuration type.

----

	.. function:: __iter__(self)

Gives an iterator over the configuration items in this configuration type.

- Return: An iterator over the configuration items in this configuration type.

----

	.. function:: load(self, directory)

Loads all of the configuration instance from a specified directory. This overwrites all configuration items in the configuration type by the configuration that the string represents.

The directory to load the configuration from is given by the framework. It will be provided specifically for the configuration plug-in, so no other function should have access to that directory. This is not enforced however, and it is advisable to access only data within the confines of the specified directory and its subdirectories.

- ``directory``: The directory containing serialised configuration data to load the configuration from.
- Raises: ``ConfigurationError`` if the provided configuration is not a well-formed representation of any configuration state.

----

	.. function:: save(self, directory)

Saves the current configuration state to a specified directory. This method should be a snapshot of the configuration state, meaning that it should be atomic and not save a representation of a state of the configuration that never existed at a single point in time.

The directory to save the configuration to is given by the framework. It will be provided specifically for the configuration plug-in, so no other function should have access to that directory. This is not enforced, however, and it is advisable to access only data within the confines of the specified directory and its subdirectories.

- ``directory``: The directory to save the configuration data to.