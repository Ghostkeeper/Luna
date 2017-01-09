#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
A persistent storage plug-in that writes and reads to local file storage.

These operations are done on the local hard drive.
"""

import localstorage.local_storage #The storage implementation.

def metadata():
	"""
	Provides the metadata for the local storage plug-in.
	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Local Storage",
		"description": "Enables reading and writing files on the local hard disk.",
		"version": 2,
		"dependencies": {
			"storagetype": {
				"version_min": 3,
				"version_max": 3
			},
		},

		"storage": {
			"can_read": localstorage.local_storage.can_read,
			"can_write": localstorage.local_storage.can_write,
			"delete": localstorage.local_storage.delete,
			"exists": localstorage.local_storage.exists,
			"move": localstorage.local_storage.move,
			"open_read": localstorage.local_storage.open_read,
			"open_write": localstorage.local_storage.open_write
		}
	}