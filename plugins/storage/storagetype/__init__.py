#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides functionality to save and load data to a persistent storage location.

This could be used to retain data between multiple runs of the application, such
as user preferences, or it could be used to gain additional input from an
external source, such as the file system, or save the output to a place where
other applications can access it.

The API of this plug-in type is based on "files" with a unique URI. If the
storage intended is not based on URI, a plug-in may have to emulate it and
devise a custom scheme for the URI.
"""

import storagetype.storage #The API for other plug-ins to use storage with.
import storagetype.storageregistrar #Where storage plug-ins must register.

def metadata():
	"""
	Provides the metadata for the StorageType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Storage Type",
		"description": "Defines a type of plug-in that stores and loads data to and from a persistent storage location.",
		"version": 2,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "storage",
			"api": storagetype.storage,
			"register": storagetype.storageregistrar.register,
			"unregister": storagetype.storageregistrar.unregister,
			"validate_metadata": storagetype.storageregistrar.validate_metadata
		}
	}