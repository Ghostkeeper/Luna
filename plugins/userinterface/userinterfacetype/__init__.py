#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the concept of user interfaces.

This allows for the creation of plug-ins that provide user interfaces. These do
not necessarily need to be graphical user interfaces. A user interface is simply
a routine that will show something to the user and possibly allow the user to
communicate to the application.

The plug-in registers an API to launch the user interface with, and to allow
"""

import userinterfacetype.userinterface #The API for other plug-ins to use the user interface with.
import userinterfacetype.userinterfaceregistrar #Where user interface plug-ins must register.

def metadata():
	"""
	Provides metadata for the UserInterfaceType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:return: Dictionary of metadata.
	"""
	return {
		"name": "User Interface Type",
		"description": "Defines a type of plug-in that communicates with the user by showing information to the user and allowing the user to control the application.",
		"version": 2,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "userinterface",
			"api": userinterfacetype.userinterface,
			"register": userinterfacetype.userinterfaceregistrar.register,
			"unregister": userinterfacetype.userinterfaceregistrar.unregister,
			"validate_metadata": userinterfacetype.userinterfaceregistrar.validate_metadata
		}
	}