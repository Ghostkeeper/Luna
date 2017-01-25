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

	def test_listen_all_fields(self):
		"""
		Tests listening to all changes of an instance.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self)
		self.field_integer = 1
		listener.assert_called_once_with("field_integer", 1)
		self.field_string = "I love you."
		listener.assert_called_with("field_string", "I love you.")

	def test_listen_new_fields(self):
		"""
		Test listening to all changes of an instance and then making new fields.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self)
		self.field_float = 3.1416 #pylint: disable=attribute-defined-outside-init
		listener.assert_called_once_with("field_float", 3.1416)
		delattr(self, "field_float") #Clean-up.

	def test_listen_nochange(self):
		"""
		Tests that the listener doesn't get called if the state doesn't change.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self, "field_integer")
		self.field_integer = 0 #Equal to starting state.
		listener.assert_not_called()

	def test_listen_simple(self):
		"""
		Tests a simple happy path with a single state change and single
		listener.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self, "field_integer")
		self.field_integer = 1 #Triggers a change.
		listener.assert_called_once_with("field_integer", 1)

	def test_listen_twice(self):
		"""
		Tests listening for two consecutive state changes.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self, "field_integer")
		self.field_integer = 1
		listener.assert_called_once_with("field_integer", 1)
		self.field_integer = 0 #Trigger two changes.
		listener.assert_called_with("field_integer", 0)
		self.assertEqual(listener.call_count, 2, "The state was changed twice.")