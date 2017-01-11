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