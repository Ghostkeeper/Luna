#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines a class that represents a single preference.
"""

import luna.plugins #To find the data type of the default values.

class Preference:
	"""
	Represents a single preference setting.

	A named tuple would normally suffice, but since we want to listen to changes
	in this model, a named tuple is impossible.
	"""

	def __init__(self, name, description, default_value):
		"""
		Creates a new preference object.
		:param name: A human-readable name for the preference.
		:param description: A more elaborate description by which to use the
		preference.
		:param default_value: The initial value of the preference.
		"""
		self.name = name #A human-readable name for the preference.
		self.description = description #A more elaborate description by which to use the preference.
		self.data_type = luna.plugins.api("data").type_of(default_value) #The data type of the value. The data type for new values is checked against to make sure this doesn't change.
		self.default_value = default_value #The default value for the preference, to be able to restore the defaults.
		self.value = default_value #The current value of the preference. Initialise to the default value.