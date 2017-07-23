#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validated dictionary.
"""

import configurationtype.validated_dictionary #The module we're testing.
import luna.tests #For parametrised tests.

class TestValidatedDictionary(luna.tests.TestCase):
	"""
	Collection of tests for the ``ValidatedDictionary``.
	"""

	@classmethod
	def setUp(self):
		"""
		Creates a fixture dictionary to test on.
		"""
		self.empty = configurationtype.validated_dictionary.ValidatedDictionary()

	def test_add_bad_default(self):
		"""
		Tests adding an item where the default doesn't validate.
		"""
		with self.assertRaises(ValueError):
			self.empty.add("bananas", -2, lambda n: n > 0)
		self.assertNotIn("bananas", self.empty, "When the default is invalid, the item must not get added.")

	def test_add_no_validation(self):
		"""
		Tests the simple case where the value is not validated.
		"""
		self.empty.add("apples", 4)
		#Test setting the item to a few various sorts of values to make sure it isn't validated.
		self.empty["apples"] = 4
		self.empty["apples"] = "3"
		self.empty["apples"] = None
		self.empty["apples"] = lambda x: x ** 2

	@luna.tests.parametrise({
		"two_parameters": {"function": lambda x, y: x * y > 0},
		"zero_parameters": {"function": lambda: False}
	})
	def test_add_not_a_predicate(self, function):
		"""
		Tests what happens when you provide something that is not a predicate.
		"""
		with self.assertRaises(ValueError):
			self.empty.add("oranges", 2, function)
		self.assertNotIn("oranges", self.empty, "When the validator is not a predicate, the item must not get added.")

	def test_add_validate_positive(self):
		"""
		Tests adding an item with a simple validation function.
		"""
		self.empty.add("pears", 4, lambda n: n > 0)
		#Test setting the item to a few good values.
		self.empty["pears"] = 2
		self.empty["pears"] = 1
		#Test setting the item to a few bad values.
		with self.assertRaises(ValueError):
			self.empty["pears"] = 0
		with self.assertRaises(ValueError):
			self.empty["pears"] = -5
		self.assertEqual(self.empty["pears"], 1, "The value must not change when setting an item to an invalid value.")

	def test_add_validate_type(self):
		"""
		Tests adding an item with a type-validator.

		This is probably the most common case for the validator.
		"""
		self.empty.add("kiwis", 6, lambda n: isinstance(n, int))
		#Test setting the item to a few good values.
		self.empty["kiwis"] = 0
		self.empty["kiwis"] = 10
		self.empty["kiwis"] = -4
		#Test setting the item to a few bad values.
		with self.assertRaises(ValueError):
			self.empty["kiwis"] = 0.5 #Float, not int.
		with self.assertRaises(ValueError):
			self.empty["kiwis"] = "tasty" #String, not int.
		self.assertEqual(self.empty["kiwis"], -4, "The value must not change when setting an item to an invalid value.")