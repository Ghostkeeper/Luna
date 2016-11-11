#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests for each storage plug-in whether it properly implements the storage
interface.
"""

import plugins #The main plug-ins directory.
import luna.plugins #To get the plug-ins to test with.
import luna.test_case

for plugin_path in plugins.__path__:
	luna.plugins.add_plugin_location(plugin_path)
luna.plugins.discover()

#Dynamically prepare the parameters for the parametrised tests.
can_read_parameters = {}
for identity, metadata in luna.plugins.plugins_by_type["storage"].items():
	can_read_function = metadata["storage"]["can_read"]
	can_read_parameters["abs_path_" + identity] =     {"can_read": can_read_function, "uri": "file:/path/to/file.ext"}
	can_read_parameters["full_path_" + identity] =    {"can_read": can_read_function, "uri": "frag://auth/path/path/file.ext?query=value#fragment"}
	can_read_parameters["relative_" + identity] =     {"can_read": can_read_function, "uri": "relative/path/file.ext"}
	can_read_parameters["backslash_" + identity] =    {"can_read": can_read_function, "uri": "\\\\path\\with\\backslashes"}
	can_read_parameters["invalid_auth_" + identity] = {"can_read": can_read_function, "uri": "https://[invalid_auth/file.ext"} #urllib.parse.parseurl gives a ValueError here.
	can_read_parameters["empty_" + identity] =        {"can_read": can_read_function, "uri": ""}

can_read_exception_parameters = {}
for identity, metadata in luna.plugins.plugins_by_type["storage"].items():
	can_read_function = metadata["storage"]["can_read"]
	can_read_exception_parameters["number_" + identity] = {"can_read": can_read_function, "uri": 42,   "exception": Exception}
	can_read_exception_parameters["none_" + identity] =   {"can_read": can_read_function, "uri": None, "exception": Exception}

can_write_parameters = {}
for identity, metadata in luna.plugins.plugins_by_type["storage"].items():
	can_write_function = metadata["storage"]["can_write"]
	can_write_parameters["abs_path_" + identity] =     {"can_write": can_write_function, "uri": "file:/path/to/file.ext"}
	can_write_parameters["full_path_" + identity] =    {"can_write": can_write_function, "uri": "frag://auth/path/path/file.ext?query=value#fragment"}
	can_write_parameters["relative_" + identity] =     {"can_write": can_write_function, "uri": "relative/path/file.ext"}
	can_write_parameters["backslash_" + identity] =    {"can_write": can_write_function, "uri": "\\\\path\\with\\backslashes"}
	can_write_parameters["invalid_auth_" + identity] = {"can_write": can_write_function, "uri": "https://[invalid_auth/file.ext"} #urllib.parse.parseurl gives a ValueError here.
	can_write_parameters["empty_" + identity] =        {"can_write": can_write_function, "uri": ""}

can_write_exception_parameters = {}
for identity, metadata in luna.plugins.plugins_by_type["storage"].items():
	can_write_function = metadata["storage"]["can_write"]
	can_write_exception_parameters["number_" + identity] = {"can_write": can_write_function, "uri": 42,   "exception": Exception}
	can_write_exception_parameters["none_" + identity]   = {"can_write": can_write_function, "uri": None, "exception": Exception}

class TestIntegration(luna.test_case.TestCase):
	"""
	Tests for each storage plug-in whether it properly implements the storage
	interface.
	"""

	@luna.test_case.parametrise(can_read_parameters)
	def test_can_read(self, can_read, uri):
		"""
		Tests the can_read function with normal parameters.

		The can_read function must always return a boolean answer in that case.

		:param can_read: The can_read function to test.
		:param uri: The URI to feed to the can_read function.
		"""
		self.assertIsInstance(can_read(uri), bool) #These must always give True or False as answer.

	@luna.test_case.parametrise(can_read_exception_parameters)
	def test_can_read_exception(self, can_read, uri, exception):
		"""
		Tests the can_read function with faulty parameters.

		The can_read function must raise an exception in that case.

		:param can_read: The can_read function to test.
		:param uri: The URI to feed to the can_read function.
		:param exception: The exception the function is expected to raise.
		"""
		with self.assertRaises(exception):
			can_read(uri)

	@luna.test_case.parametrise(can_write_parameters)
	def test_can_write(self, can_write, uri):
		"""
		Tests the can_write function with normal parameters.

		The can_write function must always return a boolean answer in that case.

		:param can_write: The can_write function to test.
		:param uri: The URI to feed to the can_write function.
		"""
		self.assertIsInstance(can_write(uri), bool) #These must always give True or False as answer.

	@luna.test_case.parametrise(can_write_exception_parameters)
	def test_can_write_exception(self, can_write, uri, exception):
		"""
		Tests the can_write function with faulty parameters.

		The can_write function must raise an exception in that case.

		:param can_write: The can_write function to test.
		:param uri: The URI to feed to the can_write function.
		:param exception: The exception the function is expected to raise.
		"""
		with self.assertRaises(exception):
			can_write(uri)