#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a class that allows for creating global application preferences.
"""

import luna.plugins #To get the configuration data type to extend from.

class Preferences:
	"""
	Offers a system to create global application preferences.
	"""

	def prepare(self):
		"""
		Finalizes the class initialisation using data that is only available at
		run time.
		"""
		original_class = self.__class__
		parent_class = luna.plugins.api("configuration").Configuration
		self.__class__ = original_class.__class__(original_class.__name__ + "Configuration", (original_class, parent_class), {}) #Add the configuration class mixin.