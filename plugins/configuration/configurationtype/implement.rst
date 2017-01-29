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
The configuration instance is an object that basically implements the configuration type you provide. To make all configuration types behave the same externally, the implementation of a configuration instance must have the methods listed below.

It is not advisable to create additional methods or functions on your instance unless they begin with an underscore. Doing so may introduce name clashes with the configuration items in your configuration type.

----

	.. function:: __getattr__(self, attribute)

Gets the value of a configuration item. Only the value is returned, no other metadata.

- ``attribute``: The identifier of the configuration item to get.
- Returns: The value of the configuration item.
- Raises ``AttributeError``: No configuration item with the specified identifier exists.

----

	.. function:: __iter__(self)

Creates an iterator over the identifiers of the configuration items. This allows external components to list all items, in a specific order if necessary. This is also used by the configuration API to implement filtering queries on the configuration.

- Returns: An iterator object that iterates over the configuration items.

----

	.. function:: __setattr__(self, attribute, value)

Changes the value of a configuration item. Only the value is changed, no other metadata. Which values are allowed is specified during the definition phase. Specifically, changing the data type of a configuration item should generally be disallowed in order to allow external plug-ins to better access and use the data.

This method should not allow adding new attributes. If a configuration item is set that doesn't exist yet, an ``AttributeError`` should be raised. Creating new configuration items is solely the right of the ``_define`` and ``_deserialise`` methods.

- ``attribute``: The identifier of the configuration item to change.
- ``value``: The new value for the configuration item.
- Raises ``AttributeError``: No configuration item with the specified identifier exists.

----

	.. function:: _define(self, identifier, ...)

Adds a new configuration item. The precise parameters of this function are left to the implementation of the configuration type. The user of the configuration type is expected to be dependent on the configuration type in order to know what these parameters are.

If identifiers are used via attribute access, they should adhere to the `syntax of a Python identifier`_. This is not required however. Any string may be used by the identifier unless a configuration type forbids it. Just be aware that attribute access becomes impossible if an identifier contains characters that are not allowed in a Python identifier. An example of a situation where these characters may be allowed is when the user provides the identifier of a configuration item. The configuration item can then only be obtained through iteration or via the ``getattr`` built-in function. Additionally, all identifiers starting with an underscore are forbidden in order to prevent name clashes with methods. If the identifiers are directly provided by a user, it is advised to use a prefix in the attribute name that is stored in the instance, which is removed again when the item is shown to the user.

This method is the place to perform checks on the configuration item as well, such as whether the item has a data type that is allowed. If this is not allowed, the method may raise arbitrary exceptions. The component that uses the configuration type must know what these exceptions are in order to catch them.

- ``identifier``: The identifier of the new configuration item.
- ... This method may have any arbitrary parameters.
- Raises ``Exception``: The definition is invalid for this configuration type.

.. _syntax of a Python identifier: https://docs.python.org/3/reference/lexical_analysis.html#identifiers

----

	.. function:: _load(self, directory)

Loads all of the configuration instance from a specified directory. This overwrites all configuration items in the configuration type by the configuration that the contents of the directory represent.

The directory to load the configuration from is given by the framework. It will be provided specifically for the configuration type, so no other function should have access to that directory and no data should be present. This is not enforced however, and it is strongly advised to access only data within the confines of the specified directory and its subdirectories and treat the data within with distrust.

- ``directory``: The directory containing serialised configuration data to load the configuration from.
- Raises: ``ConfigurationError`` if the provided configuration is not a well-formed representation of any configuration state.

----

	.. function:: _metadata(self, identifier)

Gets a dictionary of the metadata of the configuration instance. This metadata should contain all information provided in the ``_define`` method any additional metadata that may be useful. This is also used by the configuration API to implement query filtering.

A few metadata keys are reserved. These should not appear in your metadata dictionaries:

- ``value``. This is reserved for the current value of the configuration item in filter queries.
- ``key``. This is reserved for the identifier of the configuration item in filter queries.
- ``type``. This is reserved for the identifier of the configuration type you're implementing in filter queries.

All configuration items should have the same metadata entries. This makes formulating queries easier for components that query on metadata. This is not a hard requirement though.

- ``identifier``: The identifier of the configuration item to get the metadata of.
- Return: A dictionary of the metadata of your configuration item.

----

	.. function:: _save(self, directory)

Saves the current configuration state to a specified directory. This method should be a snapshot of the configuration state, meaning that it should be atomic and not save a representation of a state of the configuration that never existed at a single point in time.

The directory to save the configuration to is given by the framework. It will be provided specifically for the configuration plug-in, so no other function should have access to that directory. This is not enforced however, and it is strongly advised to access only data within the confines of the specified directory and its subdirectories.

This may save the configuration all into one file, or into many, using as many subdirectories as necessary.

- ``directory``: The directory to save the configuration data to.
- Raises ``OSError``: The configuration could not be saved for some reason.

----------------------------------------
Configuration instance: Optional methods
----------------------------------------
The following methods may improve the functionality or performance of your configuration type, but they are not required.

----

	.. function:: __delattr__(self, attribute)

Removes a configuration item with the specified identifier.

If not implemented, the user of this configuration type should expect a ``TypeError`` (because the method doesn't exist). Do not implement this and then return a ``NotImplementedError``.

- ``attribute``: The identifier of the configuration item to change.

----

	.. function:: __len__(self)

Returns the number of configuration items in this configuration type.

If this is not implemented, the length is automatically obtained by iterating over the configuration items. This may be inefficient, so providing this method can improve performance.

- Return: The number of configuration items in this configuration type.

----

	.. function:: __contains__(self, item)

Returns whether this configuration type contains a configuration item with the specified identifier.

If this is not implemented, it is found by iterating over the configuration items. This may be inefficient, so providing this method can improve performance.

- ``item``: The identifier of the configuration item to test for.
- Return: ``True`` if a configuration item exists with the specified identifier, or ``False`` if no such item exists.