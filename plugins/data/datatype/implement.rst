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

Turns the serialised ``bytes``, which represent a state of being of an instance of this data type, into an instance of this data type with that state.

- ``serialised``: The ``bytes`` that represent the state of an instance of the data type.
- Return: An instance of the data type that the serialised ``bytes`` represented.

----

	.. function:: is_instance(data)

Checks if a data object is of the data type that the plug-in implements.

- ``data``: The object to check for.
- Return: ``True`` if the object is of this data type, or ``False`` if it isn't.

----

	.. function:: is_serialised(serialised)

Checks if the specified ``bytes`` represent an object of the data type that the plug-in implements.

For performance reasons, it is important to check this fairly efficiently, since every data type must be tested in order to find the data type of a sequence of bytes. Use a magic number if available.

- ``serialised``: ``bytes`` representing some object.
- Return: ``True`` if the sequence of bytes represents an object of this data type, or ``False`` if it doesn't.

----

	.. function:: serialise(data)

Serialises an instance of the data type into ``bytes`` for storage or communication.

- ``data``: The instance of the data type.
- Return: A ``bytes`` object that represents the state of the instance completely.

---------
MIME Type
---------
A data type may specify an optional MIME type. If it does, the data should be considered fit to be stored in a file (by itself). This opens the way for registering the file to be opened with the application, and allowing for tricks like dropping the file onto the window of the application to open it.

To implement a MIME type, the following metadata entries must be provided in addition to the functionality listed above.

- ``mimetype``: The media type identifier as specified by `RFC 6838`_. For example ``text/plain`` or ``application/x-luna-preferences``.
- ``name``: A human-readable name in English for the media type. For example ``Plain text`` or ``Luna preferences``.

Additionally, the ``extensions`` entry may optionally be provided in order to specify any file extensions belonging to the media type. File dialogues may make use of these extensions to filter files. This must be a sequence of strings. The sequence may be empty, in which case the entry is ignored. If not defined or empty, files containing this data type are assumed to have no extension. The extensions do not include the period in front (so use ``txt`` instead of ``.txt``) but may contain periods if multiple extensions are desired (as in ``tar.gz``).

.. _`RFC 6838`: https://tools.ietf.org/html/rfc6838