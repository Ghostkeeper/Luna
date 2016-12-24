.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

==========================
Implementing data plug-ins
==========================
This document gives instructions on how to implement a data plug-in. A data plug-in defines a type of data. Other plug-ins can then claim that they support that type of data or some version of it. Additionally, the plug-in defines a way to serialise and deserialise that type of data. While its aim is to not place any restrictions on how the data is used, serialising and deserialising is required in order to be able to send the data across multiple processes in any process pool, which makes the application potentially more efficient.

To implement a data plug-in, one needs to implement all functions listed below in `Required functionality`_. The metadata then needs to include an entry for each of these functions, with as key the function name and as value the function itself.

----------------------
Required functionality
----------------------
These are the functions that need to be implemented by a data plug-in. All of these functions must be in the metadata of the plug-in, indexed by the function name.

----

	.. function:: deserialise(serialised)

Turns a serialised sequence of ``bytes``, which represents a state of being of an instance of this data type, into an instance of this data type with that state.

- ``serialised``: A sequence of ``bytes`` that represents the state of an instance of the data type.
- Return: An instance of the data type that the serialised sequence represented.

----

	.. function:: is_instance(data)

Checks if a data object is of the data type that the plug-in implements.

- ``data``: The object to check for.
- Return: ``True`` if the object is of this data type, or ``False`` if it isn't.

----

	.. function:: is_serialised(serialised)

Checks if a sequence of bytes is of the data type that the plug-in implements.

For performance reasons, it is important to check this fairly efficiently using as few bytes from the source sequence as possible. Generating bytes from the source sequence may involve slow I/O. Use a magic number if available.

- ``serialised``: A sequence of bytes representing some object.
- Return: ``True`` if the sequence of bytes represents an object of this data type, or ``False`` if it doesn't.

----

	.. function:: serialise(data)

Serialises an instance of the data type into a stream of ``bytes`` for storage or communication.

- ``data``: The instance of the data type.
- Return: A stream of ``bytes`` that represents the state of the instance completely.