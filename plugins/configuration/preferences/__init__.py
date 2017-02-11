#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides global application preferences.

This allows the user to personalise the general workings and look of the
application to his liking. Other components can register preferences with this
plug-in in order to preserve the state of a variable over multiple runs of the
application.
"""

import preferences.preferences as preferences_module #The module containing the class that implements the preferences.

def metadata():
	"""
	Provides the metadata for the Preferences plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Preferences",
		"description": "Allows storing and modifying general application preferences.",
		"version": 1,
		"dependencies": {
			"configurationtype": {
				"version_min": 1,
				"version_max": 1
			},
			"datatype": {
				"version_min": 1,
				"version_max": 1
			}
		},

		"configuration": {
			"name": "preferences",
			"instance": preferences_module.Preferences()
		}
	}