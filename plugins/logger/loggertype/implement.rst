============================
Implementing logger plug-ins
============================

This document gives instruction on how to implement a logger plug-in. A logger plug-in represents one way to output log messages. Adding more loggers causes logs to be output to multiple places simultaneously.

To implement a logger plug-in, one needs to implement all functions listed below in `Function implementation`_. The metadata then needs to include an entry for each of these functions, with as key the function name and as value the function itself.

----------
Log levels
----------
There are a number of log levels that a logger plug-in should support. They each represent a certain severity. This implies an order (from severe to unimportant), but this order is only semantic and needs not be retained. For instance, a plug-in may be set to log only errors and information but not critical messages and warnings. The plug-in doesn't need to implement this filtering itself. This is done by the API, so only levels that are set to be logged by your logger are called by the API.

The log levels that are available are:
- Error, for events that prevent the entire program from properly functioning.
- Critical, for events that prevent the current operation from properly functioning.
- Warning, for when something happens that was probably not intended.
- Information, indicating an event that was initiated on purpose by an external force such as the user.
- Debug, giving detailed information on what is happening inside the application.

The logger may display these messages differently depending on the log level, such as with colour coding.

----------------------
Required functionality
----------------------
These are the functions that need to be implemented by a logger plug-in. All of these functions must be in the metadata of the plug-in, indexed by the function name.

::

	critical(message[, title])

Logs a critical message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.

----
::

	debug(message[, title])

Logs a debug message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.

----
::

	error(message[, title])

Logs an error message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.

----
::

	info(message[, title])

Logs an information message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.

----
::

	warning(message[, title])

Logs a warning message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.