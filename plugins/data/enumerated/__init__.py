#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a data type for enumerated types.

Enumerated types are abstract values that are restricted to have one of the
values from a pre-defined set of allowed values.

They are implemented using Python's ``enum`` package with one additional
restriction: All enumerated values must be unique strings. This is required to
deserialise the values back to their original instances.
"""

import enumerated.enumerated_type #The functions that implement the data type.

def metadata():
	"""
	Provides the metadata for the Data Type plug-in.

	This gives human-readable information on the plug-in, dependency resolution
	information, and tells the plug-in system what this plug-in can do.
	:return: Dictionary of metadata.
	"""
	return {
		"name": "Enumerated",
		"description": "Defines enumerated values to be used as communication between application components.",
		"version": 1,
		"dependencies": {
			"datatype": {
				"version_min": 1,
				"version_max": 1
			}
		},

		"data": {
			"serialise": enumerated.enumerated_type.serialise,
			"deserialise": enumerated.enumerated_type.deserialise,
			"is_instance": enumerated.enumerated_type.is_instance,
			"is_serialised": enumerated.enumerated_type.is_serialised
		}
	}