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

	def test_listen_simple(self):
		"""
		Tests a simple happy path with a single state change and single
		listener.
		"""
		listener = unittest.mock.MagicMock()
		luna.listen.listen(listener, self, "field_integer")
		self.field_integer = 1 #Triggers a change.
		listener.assert_called_once_with("field_integer", 1)