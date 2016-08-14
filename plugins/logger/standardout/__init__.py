#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
A logger plug-in that logs to the standard output channel.
"""

import standardout.standard_out #Implementing functions.

def metadata():
	"""
	Provides the metadata for the StandardOut plug-in.

	:returns: Dictionary of metadata.
	"""
	return {
		"name": "Standard Out",
		"description": "Outputs log messages through standard out.",
		"version": 5,
		"dependencies": {
			"loggertype": {
				"version_min": 1,
				"version_max": 1
			},
		},

		"logger": {
			"critical": standardout.standard_out.critical,
			"debug": standardout.standard_out.debug,
			"error": standardout.standard_out.error,
			"info": standardout.standard_out.info,
			"warning": standardout.standard_out.warning
		}
	}