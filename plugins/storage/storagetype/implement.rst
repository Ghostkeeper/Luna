.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

=============================
Implementing storage plug-ins
=============================
This document gives instructions on how to implement a persistent storage plug-in. A persistent storage plug-in provides functionality to read and write to a storage location that persists when the application is closed down.

To implement a storage plug-in, one needs to implement all functions listed below in `Required functionality`_. The metadata then needs to include an entry for each of these functions, with as key the function name and as value the function itself.

--------------------------------
URIs and which plug-in gets used
--------------------------------
Every storage plug-in provides two functions that allow the storage API to gauge the functionality of the plug-in: ``can_read`` and ``can_write``. These determine respectively for a URI whether the storage plug-in can read from such a URI and whether it can write to it. These functions are meant to be implemented without actually trying to read or write anything on the device the URI points to. Ability to read or write should be determined purely on the URI itself. Based on this information, the API selects a plug-in that says it can read or write the URI, depending on what type of operation is necessary.

The ``can_read`` and ``can_write`` functions should be fast. That means that they should make their judgement purely based on the URI. They should not check for existence of the file, permissions, or anything of the sort.

----------------------
Required functionality
----------------------
These are the functions that need to be implemented by a storage plug-in. All of these functions must be in the metadata of the plug-in, indexed by the function name.

----

	.. function:: can_read(uri)

Determines whether the storage plug-in can read data from the specified URI.

- ``uri``: An absolute URI for which the ability to read needs to be determined.
- Return: ``True`` if the plug-in can read from such a URI, or ``False`` if it can't.

----

	.. function:: can_write(uri)

Determines whether the storage plug-in can write data to the specified URI.

- ``uri``: An absolute URI for which the ability to write needs to be determined.
- Return: ``True`` if the plug-in can write to such a URI, or ``False`` if it can't.

----

	.. function:: delete(uri)

Removes a resource from the specified URI.

- ``uri``: An absolute URI whose resources needs to be deleted.
- Raises: ``IOException`` if the resource could not be deleted.

----

	.. function:: exists(uri)

Checks if a resource exists at the specified URI.

- ``uri``: An absolute URI for which needs to be checked if a resource exists.
- Return: ``True`` if the resource exists, or ``False`` if it doesn't.
- Raises: ``IOException`` if the check could not be performed.

----

	.. function:: move(source, destination)

Moves data from one place to another.

If there is already a resource at the destination, that resource will be lost.

- ``source``: An absolute URI to the resource that must be moved.
- ``destination``: An absolute URI to the location where the resource must be moved.
- Raises: ``IOException`` if the move could not be performed.

----

	.. function:: open_read(uri)

Opens a stream of binary data from the specified location.

- ``uri``: An absolute URI to a resource that must be read.
- Return: A stream of ``bytes`` that read from the specified location.
- Raises: ``IOException`` if the resource could not be read.

----

	.. function:: write(uri, data)

Opens a stream that writes binary data to the specified location.

If there is already a resource at the specified URI, that resource will be lost.

- ``uri``: An absolute URI to where the data must be written.
- Return: A stream for ``bytes`` that writes to the specified location.
- Raises: ``IOException`` if the resource could not be written to.