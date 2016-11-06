#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests for each storage plug-in whether it properly implements the storage
interface.
"""

import os.path #To get the plug-in directory.
import luna.plugins #To get the plug-ins to test with.
import luna.test_case

plugin_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..") #The main directory containing this plug-in (as well as all others we're hoping to find).
luna.plugins.add_plugin_location(plugin_base)
luna.plugins.discover()

class TestIntegration(luna.test_case.TestCase):
	"""
	Tests for each storage plug-in whether it properly implements the storage
	interface.
	"""

	@luna.test_case.parametrise(luna.plugins.plugins_by_type["storage"])
	def test_can_read(self, storage, **other_metadata):
		self.assertTrue(callable(storage["can_read"]), "The can_read function must be callable.")