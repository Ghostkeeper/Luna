.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

==========================
Implementing MIME plug-ins
==========================
This document gives instructions on how to implement a plug-in that registers a media type (also known as a MIME type). Media type registration causes the installer to register file associations with the application, and allows for tricks like dropping the file onto the window of the application and opening it with the correct plug-in.

To implement a MIME plug-in, one needs to provide the metadata described below in `Metadata`_, and provide the required functions as described in `Required functionality`_. The metadata needs to include an entry for each of these functions, with as key the function name and as value the function itself.

--------
Metadata
--------
A MIME plug-in needs at least these two entries in its metadata:

- ``mimetype``: The media type identifier as specified by `RFC 6838`_. For example ``text/plain`` or ``application/x-luna-preferences``.
- ``name``: A human-readable name in English for the media type. For example ``Plain text`` or ``Luna preferences``.

The following metadata entries are optional:

- ``extensions``: A sequence of file extensions belonging to the media type. File dialogues may make use of these extensions to filter files. If defined, this must be a sequence, such as a set, of strings. A single string is not allowed. The sequence may be empty, in which case the parameter is ignored. If not defined or empty, file dialogues are to apply no filter on files.

.. _`RFC 6838`: https://tools.ietf.org/html/rfc6838

----------------------
Required functionality
----------------------
These are the functions that need to be implemented by a MIME plug-in. All fo these functions must be in the metadata of the plug-in, indexed by the function name.

----

	.. function:: can_read(uri, input_stream)

Determines whether the specified file has the MIME type that the plug-in defines. To ascertain this, the function should make use of a magic number or something of the sort to determine the file type without scanning the entire file. If such a thing is impossible, it may determine whether the MIME type is correct by looking at the file name, such as by checking the file extension.

- ``uri``: A URI to the file that the MIME type needs to be checked for.
- ``input_stream``: An open stream that streams the content of the file.

----

	.. function:: read(input_stream)

Reads the content of the file and adds the data it represents to whatever entry collects content of that type. For instance, it could be added to the configuration of the application, or add the file to the current screen. The exact behaviour of this function is unspecified, but it could be called when the file is opened from the command line, opened with this application in the operating system, or dropped onto the application's window.

- ``input_stream``: An open stream that streams the content of the file.