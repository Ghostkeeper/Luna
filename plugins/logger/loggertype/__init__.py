#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides logging functionality, to allow creating plug-ins that log messages.
How those messages are stored or displayed may vary between loggers.

The plug-in registers an API to call upon the loggers to log messages as well as
an interface for logger plug-ins to implement.
"""

import loggertype.log #The API for other plug-ins to use loggers with.
import loggertype.loggerregistrar #Where logger plug-ins must register.

def metadata():
	"""
	Provides the metadata for the LoggerType plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Logger Type",
		"description": "Defines a type of plug-in that keeps a log of messages, intended to show what's happening behind the scenes of the application.",
		"version": 2,
		"dependencies": {},

		"type": { #This is a "plug-in type" plug-in.
			"type_name": "logger",
			"api": loggertype.log,
			"register": loggertype.loggerregistrar.register,
			"unregister": loggertype.loggerregistrar.unregister,
			"validate_metadata": loggertype.loggerregistrar.validate_metadata
		}
	}