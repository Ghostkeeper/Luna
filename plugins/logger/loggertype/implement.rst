============================
Implementing logger plug-ins
============================

A logger plug-in represents one way to output log messages. Adding more loggers causes logs to be output to multiple places simultaneously. Each logger can set their log levels individually though, so one could specify a file logger to output all types of messages while a log that's shown to the user could show only errors and warnings.

The logger plug-in provides a way to change the levels that it needs to log and a way to log messages with that level.

----------
Log levels
----------
There are a number of log levels that a logger plug-in should support. They each represent a certain severity. This implies an order (from severe to unimportant), but this order is only semantic and needs not be retained. For instance, a plug-in may be set to log only errors and information but not critical messages and warnings. The plug-in should support this.

The log levels that are available are:
- Error, for events that prevent the entire program from properly functioning.
- Critical, for events that prevent the current operation from properly functioning.
- Warning, for when something happens that was probably not intended.
- Information, indicating an event that was initiated on purpose by an external force such as the user.
- Debug, giving detailed information on what is happening inside the application.

-----------------------
Function implementation
-----------------------
These are the functions that need to be implemented by a plug-in. All of these functions need to be in the metadata of the plug-in, indicated by the function name.

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

	set_levels(levels)

Changes the levels that the logger should output. This may cause the logger to output nothing for certain message types even if the log function is called. The logger may opt to include a placeholder instead to indicate that something is hidden.

- ``levels``: A collection of levels that need to be logged. Levels not in this collection should not be logged. This must be a collection of ``log.Levels`` (see the API).

----
::

	warning(message[, title])

Logs a warning message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.