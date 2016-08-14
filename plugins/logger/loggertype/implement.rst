.. This documentation is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this documentation.
.. The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this documentation, the license provided with this documentation should be applied.

============================
Implementing logger plug-ins
============================
This document gives instructions on how to implement a logger plug-in. A logger plug-in represents one way to output log messages. Adding more loggers causes logs to be output to multiple places simultaneously.

To implement a logger plug-in, one needs to implement all functions listed below in `Required functionality`_. The metadata then needs to include an entry for each of these functions, with as key the function name and as value the function itself.

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

----

	.. function:: critical(message[, title][, stack_trace])

Logs a critical message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.
- ``stack_trace``: The stack trace at the except clause where the logging was initiated, if the logging was done in the except clause of a try-except block. This will get provided in the form of a list of FrameInfo_ objects, with the most recent frame last.

----

	.. function:: debug(message[, title][, stack_trace])

Logs a debug message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.
- ``stack_trace``: The stack trace at the except clause where the logging was initiated, if the logging was done in the except clause of a try-except block. This will get provided in the form of a list of FrameInfo_ objects, with the most recent frame last.

----

	.. function:: error(message[, title][, stack_trace])

Logs an error message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.
- ``stack_trace``: The stack trace at the except clause where the logging was initiated, if the logging was done in the except clause of a try-except block. This will get provided in the form of a list of FrameInfo_ objects, with the most recent frame last.

----

	.. function:: info(message[, title][, stack_trace])

Logs an information message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.
- ``stack_trace``: The stack trace at the except clause where the logging was initiated, if the logging was done in the except clause of a try-except block. This will get provided in the form of a list of FrameInfo_ objects, with the most recent frame last.

----

	.. function:: warning(message[, title][, stack_trace])

Logs a warning message.

- ``message``: The message that needs to be logged.
- ``title``: A title for the message.
- ``stack_trace``: The stack trace at the except clause where the logging was initiated, if the logging was done in the except clause of a try-except block. This will get provided in the form of a list of FrameInfo_ objects, with the most recent frame last.

.. _FrameInfo: https://docs.python.org/3/library/inspect.html#the-interpreter-stack