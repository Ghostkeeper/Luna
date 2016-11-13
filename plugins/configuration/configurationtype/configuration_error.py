#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a class of exceptions used to denote a false state of being for
configuration.
"""

class ConfigurationError(Exception):
	"""
	This exception denotes that something went wrong in the configuration.

	It is mostly a marker class, but also provides the type of configuration in
	which something went wrong.
	"""

	def __init__(self, message, configuration_type):
		"""
		Creates a new ConfigurationError.

		:param message: The message describing the error that occurred.
		:param configuration_type: The configuration type with which the error
		occurred.
		"""
		#Prepend the configuration type before the error message.
		super(ConfigurationError, self).__init__("{configuration_type}: {message}".format(configuration_type=configuration_type, message=message))
		self.configuration_type = configuration_type #Also store it here for debugging purposes.