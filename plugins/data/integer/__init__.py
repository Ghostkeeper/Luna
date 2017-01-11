#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a data type for integers.

Integers are countable numbers without a fractional component, not necessarily
positive.
"""

import integer.integer as integer_module #The functions that implement the data type.

def metadata():
	"""
	Provides the metadata for the Integer plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Integer",
		"description": "Defines integers to be used as communication between application components.",
		"version": 1,
		"dependencies": {
			"datatype": {
				"version_min": 1,
				"version_max": 1
			}
		},

		"data": {
			"serialise": integer_module.serialise,
			"deserialise": integer_module.deserialise,
			"is_instance": integer_module.is_instance,
			"is_serialised": integer_module.is_serialised
		}
	}