#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the listening module that provides a way to listen for state changes.
"""

import unittest #To define automatic tests.
import unittest.mock #To track how often a listener function was called.

import luna.listen #The module we're testing.

class TestListen(unittest.TestCase):
	"""
	Tests the listening module that provides a way to listen for state changes.
	"""

	def setUp(self):
		"""
		Prepares a few fields on this object of which we can track changes.
		"""
		self.field_integer = 0
		self.field_string = ""
		self.listener = unittest.mock.MagicMock()
		self.listener.reset_mock()

	def tearDown(self):
		"""
		Cleans up the object after possibly modifying it.
		"""
		if hasattr(self, "field_float"):
			delattr(self, "field_float")

	def test_listen_all_fields(self):
		"""
		Tests listening to all changes of an instance.
		"""
		luna.listen.listen(self.listener, self)
		self.field_integer = 1
		self.listener.assert_called_once_with("field_integer", 1)
		self.field_string = "I love you."
		self.listener.assert_called_with("field_string", "I love you.")

	def test_listen_new_fields(self):
		"""
		Test listening to all changes of an instance and then making new fields.
		"""
		luna.listen.listen(self.listener, self)
		self.field_float = 3.1416 #pylint: disable=attribute-defined-outside-init
		self.listener.assert_called_once_with("field_float", 3.1416)

	def test_listen_nochange(self):
		"""
		Tests that the listener doesn't get called if the state doesn't change.
		"""
		luna.listen.listen(self.listener, self, "field_integer")
		self.field_integer = 0 #Equal to starting state.
		self.listener.assert_not_called()

	def test_listen_simple(self):
		"""
		Tests a simple happy path with a single state change and single
		listener.
		"""
		luna.listen.listen(self.listener, self, "field_integer")
		self.field_integer = 1 #Triggers a change.
		self.listener.assert_called_once_with("field_integer", 1)

	def test_listen_twice(self):
		"""
		Tests listening for two consecutive state changes.
		"""
		luna.listen.listen(self.listener, self, "field_integer")
		self.field_integer = 1
		self.listener.assert_called_once_with("field_integer", 1)
		self.field_integer = 0 #Trigger two changes.
		self.listener.assert_called_with("field_integer", 0)
		self.assertEqual(self.listener.call_count, 2, "The state was changed twice.")

	def test_listen_multiple_attributes(self):
		"""
		Tests listening for two attributes and the instance at the same time.
		"""
		luna.listen.listen(self.listener, self, "field_integer")
		luna.listen.listen(self.listener, self, "field_string")
		luna.listen.listen(self.listener, self)
		self.field_integer = 1
		self.listener.assert_called_with("field_integer", 1)
		self.assertEqual(self.listener.call_count, 2, "The listener must be called once for the attribute and once for the instance.")
		self.field_string = "poo"
		self.listener.assert_called_with("field_string", "poo")
		self.assertEqual(self.listener.call_count, 4, "The listener must be called twice for two attributes and twice for the instance.")