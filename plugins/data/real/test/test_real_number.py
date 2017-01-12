#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the real number data type.

These tests are kept rather minimal, since they mostly just test the JSON
module.
"""

import unittest.mock #To replace the dependency on the data module.

import real.real_number #The module we're testing.
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

class TestRealNumber(luna.tests.TestCase):
	"""
	Tests the behaviour of various functions belonging to real numbers.
	"""
	#Ignore multiple spaces after assignment. It's used for outlining, dumb linter.
	#pylint: disable=C0326

	@luna.tests.parametrise({
		"zero":           {"serialised": b"0.0"},
		"fourtytwo":      {"serialised": b"42.0"},
		"pi":             {"serialised": b"3.1416"},
		"pi_long":        {"serialised": b"3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132"},
		"exponent":       {"serialised": b"2e4"},
		"frac_exponent":  {"serialised": b"11.5e2"},
		"uppercase_exp":  {"serialised": b"4.55E6"},
		"negative":       {"serialised": b"-3.2"},
		"very_high":      {"serialised": b"2e100"},
		"negative_exp":   {"serialised": b"3e-100"},
		"positive_exp":   {"serialised": b"7.1e+10"},
		"float_rounding": {"serialised": b"3.0"}, #Number can't be exactly represented with IEEE 754.
		"very_negative":  {"serialised": b"-1000000000000000000000000.0"} #-10^24.
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise(self, serialised):
		"""
		Tests whether we can deserialise real numbers.
		:param serialised: The serialised form of some real number.
		"""
		result = real.real_number.deserialise(luna.stream.BytesStreamReader(serialised))
		self.assertIsInstance(result, float)

	@luna.tests.parametrise({
		"empty":           {"serialised": b""},
		"not_utf_8":       {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"letters":         {"serialised": b"ghostkeeper"},
		"foreign_digits":  {"serialised": "４.0".encode("utf_8")},
		"integer":         {"serialised": b"3"},
		"imaginary":       {"serialised": b"9.8i"},
		"no_fractional":   {"serialised": b"0."},
		"no_exponent":     {"serialised": b"0.3e"},
		"no_exponent_neg": {"serialised": b"0.3e-"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_error(self, serialised):
		"""
		Tests fail cases in which the deserialisation must give an exception.
		:param serialised: Some serialised data that is not a real number.
		"""
		with self.assertRaises(luna.tests.MockException):
			real.real_number.deserialise(luna.stream.BytesStreamReader(serialised))

	@luna.tests.parametrise({
		"zero": {
			"serialised": b"0.0"
		},
		"fourtytwo": {
			"serialised": b"42.0"
		},
		"pi": {
			"serialised": b"3.1416"
		},
		"pi_long": {
			"serialised": b"3.141592653589793"
		},
		"exponent": {
			"serialised": b"2e4",
			"synonyms": {b"2.0e+4", b"20000.0"}
		},
		"frac_exponent": {
			"serialised": b"11.5e2",
			"synonyms": {b"11.5e+2", b"1150.0"}
		},
		"uppercase_exp": {
			"serialised": b"4.55E6",
			"synonyms": {b"4.55e+6", b"4550000.0"}
		},
		"negative": {
			"serialised": b"-3.2"
		},
		"very_high": {
			"serialised": b"2e100",
			"synonyms": {b"2e+100", b"20000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"}
		},
		"negative_exp": {
			"serialised": b"3e-100",
			"synonyms": {b"0.0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000003"}
		},
		"positive_exp": {
			"serialised": b"7.1e+10",
			"synonyms": {b"71000000000.0"}
		},
		"float_rounding": {
			"serialised": b"3.0" #Number can't be exactly represented with IEEE 754.
		},
		"very_negative": {
			"serialised": b"-1000000000000000000000000.0", #-10^24.
			"synonyms": {b"-1e+24"}
		}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_serialise(self, serialised, synonyms=None):
		"""
		Tests whether deserialising and then serialising results in the same
		instance.
		:param serialised: The serialised form to start (and hopefully end up)
		with.
		:param synonyms: Other allowed serialisations representing the same
		number.
		"""
		if synonyms is None:
			synonyms = set() #Empty set as default.
		instance = real.real_number.deserialise(luna.stream.BytesStreamReader(serialised))
		new_serialised = real.real_number.serialise(instance)
		allowed_answers = {serialised} | synonyms #Allow original string as well as all synonyms.
		self.assertIn(new_serialised.read(), allowed_answers, "The serialised form {serialised} must be consistent or a synonym after deserialising and serialising.".format(serialised=str(serialised)))

	@luna.tests.parametrise({
		"zero":          {"instance": 0.0},
		"three":         {"instance": 3.0},
		"pi":            {"instance": 3.1416},
		"very_big":      {"instance": 2e65},
		"negative":      {"instance": -42.0},
		"very_small":    {"instance": 3e-100},
		"very_negative": {"instance": -1000000000000000000000000.0} #-10^24.
	})
	def test_is_instance(self, instance):
		"""
		Tests whether it is correctly detected that these are real numbers.
		:param instance: A real number of which we must detect that it is a real
		number.
		"""
		self.assertTrue(real.real_number.is_instance(instance))

	@luna.tests.parametrise({
		"none":    {"instance": None},
		"string":  {"instance": "G"}, #G-string.
		"class":   {"instance": float},
		"bytes":   {"instance": b"3.1416"}, #The serialised form of a real number, but not the real number itself.
		"integer": {"instance": 5}, #Technically a real number, but we don't want to identify it as such since that would give confusion for detecting integers.
		"object":  {"instance": luna.tests.CallableObject()}
	})
	def test_is_not_instance(self, instance):
		"""
		Tests whether it is correctly detected that these are not real numbers.
		:param instance: Not a real number.
		"""
		self.assertFalse(real.real_number.is_instance(instance))

	@luna.tests.parametrise({
		"empty":           {"serialised": b""},
		"not_utf_8":       {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"letters":         {"serialised": b"ghostkeeper"},
		"foreign_digits":  {"serialised": "４.0".encode("utf_8")},
		"integer":         {"serialised": b"3"},
		"imaginary":       {"serialised": b"9.8i"},
		"no_fractional":   {"serialised": b"0."},
		"no_exponent":     {"serialised": b"0.3e"},
		"no_exponent_neg": {"serialised": b"0.3e-"},
		"minus":           {"serialised": b"-"},
	})
	def test_is_not_serialised(self, serialised):
		"""
		Tests whether bytes streams that don't represent real numbers are
		identified as such.
		:param serialised: A sequence of bytes that doesn't represent a real
		number.
		"""
		self.assertFalse(real.real_number.is_serialised(luna.stream.BytesStreamReader(serialised)), "{serialised} must not be identified as a serialised real number.".format(serialised=str(serialised)))

	@luna.tests.parametrise({
		"zero":           {"serialised": b"0.0"},
		"fourtytwo":      {"serialised": b"42.0"},
		"pi":             {"serialised": b"3.1416"},
		"pi_long":        {"serialised": b"3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132"},
		"exponent":       {"serialised": b"2e4"},
		"frac_exponent":  {"serialised": b"11.5e2"},
		"uppercase_exp":  {"serialised": b"4.55E6"},
		"negative":       {"serialised": b"-3.2"},
		"very_high":      {"serialised": b"2e100"},
		"negative_exp":   {"serialised": b"3e-100"},
		"positive_exp":   {"serialised": b"7.1e+10"},
		"float_rounding": {"serialised": b"3.0"}, #Number can't be exactly represented with IEEE 754.
		"very_negative":  {"serialised": b"-1000000000000000000000000.0"} #-10^24.
	})
	def test_is_serialised(self, serialised):
		"""
		Tests whether serialised forms of real numbers are correctly identified
		as such.
		:param serialised: A correct serialised form of a real number.
		"""
		self.assertTrue(real.real_number.is_serialised(luna.stream.BytesStreamReader(serialised)), "{serialised} must be identified as a serialised real number.".format(serialised=str(serialised)))

	@luna.tests.parametrise({
		"zero":          {"instance": 0.0},
		"three":         {"instance": 3.0},
		"pi":            {"instance": 3.1416},
		"very_big":      {"instance": 2e65},
		"negative":      {"instance": -42.0},
		"very_small":    {"instance": 3e-100},
		"very_negative": {"instance": -1000000000000000000000000.0} #-10^24.
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise(self, instance):
		"""
		Tests whether we can serialise integers.
		:param instance: The integer to serialise.
		"""
		result = real.real_number.serialise(instance)
		for byte in result:
			self.assertIsInstance(byte, int, "The serialised real number for {instance} must be a byte sequence.".format(instance=str(instance)))
		self.assertTrue(hasattr(result, "read"), "The serialised real number for {instance} must be a byte stream.".format(instance=str(instance)))

	@luna.tests.parametrise({
		"zero":          {"instance": 0.0},
		"three":         {"instance": 3.0},
		"pi":            {"instance": 3.1416},
		"pi_long":       {"instance": 3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132},
		"very_big":      {"instance": 2e65},
		"negative":      {"instance": -42.0},
		"very_small":    {"instance": 3e-100},
		"very_negative": {"instance": -1000000000000000000000000.0} #-10^24.
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_deserialise(self, instance):
		"""
		Tests whether serialising and then deserialising results in the original
		instance.
		:param instance: The instance to start (and hopefully end up) with.
		"""
		serialised = real.real_number.serialise(instance)
		deserialised = real.real_number.deserialise(serialised)
		self.assertEqual(instance, deserialised, "The real number {instance} must be the same after serialising and deserialising.".format(instance=str(instance)))

	@luna.tests.parametrise({
		#We only want to include tests that wouldn't be JSON-serialisable. If it's JSON-serialisable, then for all that this module is concerned it quacks like a real number.
		"custom_object": {"instance": luna.tests.CallableObject()}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_error(self, instance):
		"""
		Tests fail cases in which serialisation must raise an exception.
		:param instance: An object that is not a real number.
		"""
		with self.assertRaises(luna.tests.MockException):
			real.real_number.serialise(instance)