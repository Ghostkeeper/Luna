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
The configuration instance is an instance of the class that basically implements the configuration type you provide. The instance must implement the abstract base class ``collections.abc.MutableMapping``. Furthermore, it needs to have a specific ``define`` functionality to allow creating new entries, while the normal ``__setitem__`` method disallows creating new items. The instance also requires functionality to save and load itself from a directory in persistent storage.

This is quite a lot of work. To help implement this, a base class is defined that already implements most of these, allowing for configuration in a basic tree structure. However, this base class is part of this ``configurationtype`` plug-in and you have no guarantee that the plug-in is already loaded at the point when your plug-in's metadata is evaluated. You should therefore have to swap out the class at runtime when the configuration type plug-in is loaded in order to satisfy the abstract base class, or otherwise face implementing all functions yourself.

The functions required are all described below. However, typical implementations should only have to overwrite the ``define`` method and the ``save`` and ``load`` methods and handle the rest through the ``Configuration`` base class.

----

	.. function:: __delitem__(self, item)

Deletes a child configuration item.

The default implementation is basically the inverse of ``define``. A more strict configuration class could for example restrict this operation to only happen in certain conditions or prevent this operation entirely.

- ``item``: The identifier of the configuration item to delete.
- Raises: ``KeyError`` if no item with the specified identifier exists in this configuration.

----

	.. function:: __getitem__(self, item)

Gets a configuration item with a specified identifier.

- ``item``: The identifier of the item to get.
- Return: The configuration item with the specified identifier.
- Raises: ``KeyError`` if no item with the specified identifier exists in this configuration.

----

	.. function:: __iter__(self)

Gives an iterator over the configuration items in this configuration.

The default implementation gives no guarantee as to the order in which items are passed.

- Return: An iterator over the configuration items in this configuration type.

----

	.. function:: __len__(self)

Returns the number of child configurations in this configuration.

- Return: The number of child configurations.

----

	.. function:: __setitem__(self, item, value)

Changes an existing configuration item to have the specified value. This should not create new configuration items, so it first needs to check if the configuration item exists and raise a ``KeyError`` if it doesn't.

- ``item``: The identifier of the item to change.
- Raises: ``KeyError`` if no item with the specified identifier exists in this configuration.

----

	.. function:: define(...)

Adds a new configuration entry as child configuration.

The parameters to this method are free for the configuration type to choose. Typically, a configuration type would require an item key, usually a default value, and perhaps a data type and validation function. But other properties may be required by the configuration type as well if more metadata is desired.

The default implementation allows only configuration types to be added and therefore doesn't require a data type.

Because the ``define`` method of different configuration types may differ, any component wanting to define new configuration entries must depend on the specific configuration type they wish to define things in, so that they know what parameters to call the ``define`` method with.

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

-------------------------
Automatically implemented
-------------------------
The following methods are automatically implemented by the ``collections.abc.MutableMapping`` abstract base class as well as by the ``Configuration`` base class. The author of a configuration type plug-in will rarely have to implement them, but they are also required:

----

	.. function:: __contains__(self, key)

Returns whether the configuration has an entry with the specified identifier.

- ``key``: The identifier to search for in this configuration.
- Return: ``True`` if an entry with the specified identifier is present, or ``False`` if it isn't.

----

	.. function:: __eq__(self, other)

Returns whether all elements in this configuration are the same as all elements in another configuration. This includes keys as well as values.

- ``other``: The configuration to compare against.
- Return: ``True`` if the configuration is exactly equal to the other configuration, or ``False`` if it isn't.

----

	.. function:: __ne__(self, other)

Returns whether this configuration is not equal to another configuration. This is typically the inverse of the ``__eq__`` method. This includes keys as well as values.

- ``other``: The configuration to compare against.
- Return: ``True`` if the configuration is not exactly equal to the other configuration, or ``False`` if it is.

----

	.. function:: get(self, key, default=None)

Returns the value of the configuration item with the given key. If no entry with the specified identifier is available, the default is returned.

- ``key``: The identifier of the item to get.
- ``default``: A value to return if no item with the specified identifier is available.
- Return: The value of the entry with the specified identifier, or the default value if no such entry is available.

----

	.. function:: items(self)

Returns a sequence of all child configuration entries as tuples of their identifier with their value.

- Return: A sequence of all child configuration items.

----

	.. function:: keys(self)

Returns a sequence of all identifiers for child configurations.

- Return: A sequence of all identifiers for child configurations.

----

	.. function:: values(self)

Returns a sequence of the values of all child configurations. They are not passed in any particular order unless your configuration type specifies it so.

- Return: A sequence of the values of all child configurations.