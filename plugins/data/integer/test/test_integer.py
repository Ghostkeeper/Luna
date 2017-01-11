#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the integer data type.

These tests are kept rather minimal, since they mostly just test the JSON
module.
"""

import unittest.mock #To replace the dependency on the data module.

import integer.integer as integer_module #The module we're testing.
import luna.stream #To create streams of bytes as input.
import luna.tests #For parametrised tests and mock exceptions.


def mock_api(plugin_type):
	"""
	Mocks calls to different APIs.

	This allows the tests to remain unit tests, even if the actual units try to
	call upon different plug-ins.
	:param plugin_type: The type of plug-in to mock.
	:return: A fake API for that plug-in.
	"""
	mock = unittest.mock.MagicMock()
	if plugin_type == "data": #We need to specify the SerialisationException as an actual exception since the "raise" keyword is not Pythonic: It actually tests for type!
		mock.SerialisationException = luna.tests.MockException
	return mock

class TestInteger(luna.tests.TestCase):
	"""
	Tests the behaviour of various functions belonging to integers.
	"""
	#Ignore multiple spaces after assignment. It's used for outlining, dumb linter.
	#pylint: disable=C0326

	@luna.tests.parametrise({
		"zero":       {"serialised": b"0"},
		"fourtytwo":  {"serialised": b"42"},
		"septillion": {"serialised": b"1000000000000000000000000"}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"serialised": b"-99"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise(self, serialised):
		"""
		Tests whether we can deserialise integers.
		:param serialised: The serialised form of some integer.
		"""
		result = integer_module.deserialise(luna.stream.BytesStreamReader(serialised))
		self.assertIsInstance(result, int)

	@luna.tests.parametrise({
		"empty":          {"serialised": b""},
		"not_utf_8":      {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"letters":        {"serialised": b"ghostkeeper"},
		"foreign_digits": {"serialised": "４".encode("utf_8")},
		"float":          {"serialised": b"3.1416"},
		"round_float":    {"serialised": b"9.0"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_error(self, serialised):
		"""
		Tests fail cases in which the deserialisation must give an exception.
		:param serialised: Some serialised data that is not an integer.
		"""
		with self.assertRaises(luna.tests.MockException):
			integer_module.deserialise(luna.stream.BytesStreamReader(serialised))

	@luna.tests.parametrise({
		"zero":       {"instance": 0},
		"fourtytwo":  {"instance": 42},
		"septillion": {"instance": 1000000000000000000000000}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"instance": -99}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise(self, instance):
		"""
		Tests whether we can serialise integers.
		:param instance: The integer to serialise.
		"""
		result = integer_module.serialise(instance)
		for byte in result:
			self.assertIsInstance(byte, int, "The serialised integer must be a byte sequence.")
		self.assertTrue(hasattr(result, "read"), "The serialised integer must be a byte stream.")

	@luna.tests.parametrise({
		#We only want to include tests that wouldn't be JSON-serialisable. If it's JSON-serialisable, then for all that this module is concerned it quacks like an integer.
		"custom_object": {"instance": luna.tests.CallableObject()}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_error(self, instance):
		"""
		Tests fail cases in which serialisation must raise an exception.
		:param instance: An object that is not an integer.
		"""
		with self.assertRaises(luna.tests.MockException):
			integer_module.serialise(instance)