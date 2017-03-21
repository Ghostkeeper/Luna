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
		result = integer_module.deserialise(serialised)
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
			integer_module.deserialise(serialised)

	@luna.tests.parametrise({
		"zero":       {"serialised": b"0"},
		"fourtytwo":  {"serialised": b"42"},
		"septillion": {"serialised": b"1000000000000000000000000"}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"serialised": b"-99"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_serialise(self, serialised):
		"""
		Tests whether deserialising and then serialising results in the same
		instance.
		:param serialised: The serialised form to start (and hopefully end up)
		with.
		"""
		instance = integer_module.deserialise(serialised)
		new_serialised = integer_module.serialise(instance)
		self.assertEqual(serialised, new_serialised, "The serialised form must be consistent after deserialising and serialising.")

	@luna.tests.parametrise({
		"zero":       {"instance": 0},
		"fourtytwo":  {"instance": 42},
		"septillion": {"instance": 1000000000000000000000000}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"instance": -99}
	})
	def test_is_instance(self, instance):
		"""
		Tests whether it is correctly detected that these are integers.
		:param instance: An integer of which we must detect that it is an
		integer.
		"""
		self.assertTrue(integer_module.is_instance(instance))

	@luna.tests.parametrise({
		"none":   {"instance": None},
		"string": {"instance": "G"}, #G-string.
		"class":  {"instance": int},
		"bytes":  {"instance": b"42"}, #The serialised form of an integer, but not the integer itself.
		"float":  {"instance": 3.1416},
		"object": {"instance": luna.tests.CallableObject()}
	})
	def test_is_not_instance(self, instance):
		"""
		Tests whether it is correctly detected that these are not integers.
		:param instance: Not an integer.
		"""
		self.assertFalse(integer_module.is_instance(instance))

	@luna.tests.parametrise({
		"empty":          {"serialised": b""},
		"not_utf_8":      {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"letters":        {"serialised": b"ghostkeeper"},
		"foreign_digits": {"serialised": "４".encode("utf_8")},
		"float":          {"serialised": b"3.1416"},
		"round_float":    {"serialised": b"9.0"}
	})
	def test_is_not_serialised(self, serialised):
		"""
		Tests whether bytes streams that don't represent integers are identified
		as such.
		:param serialised: A sequence of bytes that doesn't represent an
		integer.
		"""
		self.assertFalse(integer_module.is_serialised(serialised), "This must not be identified as a serialised integer.")

	@luna.tests.parametrise({
		"zero":       {"serialised": b"0"},
		"fourtytwo":  {"serialised": b"42"},
		"septillion": {"serialised": b"1000000000000000000000000"}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"serialised": b"-99"}
	})
	def test_is_serialised(self, serialised):
		"""
		Tests whether serialised forms of integers are correctly identified as
		such.
		:param serialised: A correct serialised form of an integer.
		"""
		self.assertTrue(integer_module.is_serialised(serialised), "This must be identified as a serialised integer.")

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

	@luna.tests.parametrise({
		"zero":       {"instance": 0},
		"fourtytwo":  {"instance": 42},
		"septillion": {"instance": 1000000000000000000000000}, #10^24, way too large to be represented by 32-bit integers, or even 64-bit.
		"negative":   {"instance": -99}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_deserialise(self, instance):
		"""
		Tests whether serialising and then deserialising results in the original
		instance.
		:param instance: The instance to start (and hopefully end up) with.
		"""
		serialised = integer_module.serialise(instance)
		deserialised = integer_module.deserialise(serialised)
		self.assertEqual(instance, deserialised, "The integer must be the same after serialising and deserialising.")

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