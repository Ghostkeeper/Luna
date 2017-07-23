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