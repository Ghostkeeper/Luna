#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for storing and retrieving configuration data of the application.

This API is used by simple attribute getting. Each configuration type adds an
attribute to this API which itself contains attributes referring to their own
objects or to other categories. For instance, you could get the value of a
preference like this::

	luna.plugins("configuration").preferences.user_interface.language

You can change the value of a preference in a similar way::

	luna.plugins("configuration").preferences.user_interface.language = "Quenya"

A configuration item can only be get or set if it exists first. A new item can
be created by calling a function with the name of the item you'd like::

	luna.plugins("configuration").preferences.user_interface.language(
		default="Common",
		options=["Common", "Quenya", "Sindarin"]
	)

In this case, which key-word arguments may be provided to the 'constructor' is
defined by the configuration type (which is always the first attribute after the
API itself; ``preferences`` in the example above).

Getting an item that doesn't exist yields a ``TypeError``, to mimic the normal
attribute access of Python. Getting an item that is not a leaf will return an
instance of ``Configuration``, which is a base class that provides the basic
functionality described in the API above.

It is up to the plug-in how it actually stores the information given to it. It
needs not store each unique path to a unique file on the file system. It may
choose to group directories together in one file so that that file may more
easily be shared.
"""

def __getattr__(item):
	raise Exception("Not implemented yet.")

class Configuration:
	#Not implemented yet.
	pass