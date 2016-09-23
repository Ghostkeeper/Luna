#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a way to configure the application to the user's liking, and store this
configuration persistently for the user.

The plug-in registers an API that allows storing of user configuration and later
reading that configuration back.
"""

import configurationtype.configuration #The API for other plug-ins to use configuration with.
import configurationtype.configuration_registrar #Where logger plug-ins must register.

def metadata():
	"""
	Provides the metadata for the ConfigurationType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:return: Dictionary of metadata.
	"""
	return {
		"name": "Configuration Type",
		"description": "Defines a type of plug-in that stores a configuration for the application persistently.",
		"version": 1,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "configuration",
			"api": configurationtype.configuration,
			"register": configurationtype.configuration_registrar.register,
			"unregister": configurationtype.configuration_registrar.unregister,
			"validate_metadata": configurationtype.configuration_registrar.validate_metadata
		}
	}