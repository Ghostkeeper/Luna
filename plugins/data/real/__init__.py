#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a data type for real numbers.

Real numbers are represented as floating point numbers in this implementation.
"""

import real.real_number #The functions that implement the data type.

def metadata():
	"""
	Provides the metadata for the Real plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Real",
		"description": "Defines real numbers to be used as communication between application components.",
		"version": 1,
		"dependencies": {
			"datatype": {
				"version_min": 1,
				"version_max": 1
			}
		},

		"data": {
			"serialise": real.real_number.serialise,
			"deserialise": real.real_number.deserialise,
			"is_instance": real.real_number.is_instance,
			"is_serialised": real.real_number.is_serialised
		}
	}