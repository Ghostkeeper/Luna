====================================
Implementing user interface plug-ins
====================================
This document gives instructions on how to implement a user interface plug-in. A user interface interacts with the user, so it lets the user "use" the application. This includes basic things such as letting the user open a file, so this makes user interfaces actually responsible for governing the entire process through which the application goes from the moment when all plug-ins are loaded to the application's termination.

An application typically starts one user interface and lets it run until it closes itself, but multiple user interfaces might be active at the same time in some cases. In these cases, each user interface should provide its own view on the data in the model, and user interactions on each view should cause updates in all views. Multiple user interfaces might call upon each other to perform specific tasks. For instance, an application might rely on a different user interface to perform a specific operation that requires a wholly different user interface, such as saving a file to disk.

To implement a user interface plug-in, one needs to implement all functions listed below in `Required functionality`_. The metadata then needs to include an entry for each of these functions, with as key the function name and as value the function itself.

---------
Threading
---------
The user interface API has been designed with threading in mind. This allows for the creation of multiple user interfaces simultaneously, without letting one user interface freeze while another runs. Therefore, a user interface's ``run`` command should not block the current thread. Only the ``join`` command should block the thread.

If this constraint is not held, the user interface will still work, but may cause other user interfaces to freeze their main thread while running your user interface.

----------------------
Required functionality
----------------------
These are the functions that need to be implemented by a logger plug-in. All of these functions must be in the metadata of the plug-in, indexed by the function name.

----

::

	join()

Blocks the current thread until the user interface has stopped.

----

::

	start()

Starts the user interface.

Starting a user interface that has already started should have no effect, even if the user interface was stopped since. User interfaces are one-shot instances.

----

::

	stop()

Stops the user interface.

This may still give the user interface time to close down. It should behave like the SIGTERM Unix signal. The method should block the current thread until the user interface has stopped.