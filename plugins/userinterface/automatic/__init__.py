#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
A plug-in that provides a user interface which runs completely automatically.

The purpose of this user interface is to require no user interaction at all. It
just handles the process all on its own, without fuss. This makes it easy to
just run the application very quickly in a folder with some files that have to
be converted.
"""

import automatic.automatic as automatic_module #Prevent mixing up the package name and the module name!

def metadata():
	"""
	Provides the metadata for the Automatic plug-in.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Automatic",
		"description": "A user interface that automatically converts data without user interaction.",
		"version": 3,
		"dependencies": {
			"userinterfacetype": {
				"version_min": 1,
				"version_max": 1
			},
			"standardout": {
				"version_min": 5,
				"version_max": 5
			}
		},

		"userinterface": {
			"join": automatic_module.join,
			"start": automatic_module.start,
			"stop": automatic_module.stop
		},
	}