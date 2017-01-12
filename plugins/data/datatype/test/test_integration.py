#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests for each data plug-in whether it properly implements the data interface.
"""

import os.path #To generate the plug-in directory.
import sys #To find any plug-in directories in the Python Path.
import test.test_enum #For an example enumerated type.

import luna.plugins #To get the plug-ins to test with.
import luna.tests #To create parametrised tests.

for root_path in sys.path:
	plugin_path = os.path.join(root_path, "plugins")
	if os.path.exists(plugin_path):
		luna.plugins.add_plugin_location(os.path.join(root_path, "plugins"))
luna.plugins.discover()

class TestIntegration(luna.tests.TestCase):
	"""
	Tests for each data plug-in whether it properly implements the data
	interface.
	"""

	@luna.tests.parametrise({
		"none":    {"instance": None},
		"integer": {"instance": 42},
		"float":   {"instance": 3.14},
		"string":  {"instance": "Communism jokes are not funny unless everyone gets them."},
		"enum":    {"instance": test.test_enum.Fruit.banana},
		"object":  {"instance": object()}
	})
	def test_is_instance_unique(self, instance):
		"""
		Tests whether an object only gets identified as an instance of at most
		one data type.

		Being an instance of multiple data types is theoretically possible, but
		undesirable for the purpose of type detection since the result is then
		indeterminate.
		:param instance: An object of which to find the types.
		"""
		instance_of = set() #The plug-ins that this object is supposedly an instance of.
		for identity, metadata in luna.plugins.plugins_by_type["data"].items():
			is_instance = metadata["data"]["is_instance"]
			if is_instance(instance):
				instance_of.add(identity)
		self.assertLessEqual(len(instance_of), 1, "Instance {instance} is found to be an instance of multiple data types: {data_plugins}".format(instance=str(instance), data_plugins=", ".join(instance_of)))