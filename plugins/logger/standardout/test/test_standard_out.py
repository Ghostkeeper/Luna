#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the standard_out logger implementation.
"""

import io #Provides a replacement I/O channel to mock stdout.
import sys #To capture stdout.
import luna.test_case #To get parametrised tests.

import standardout.standard_out #The module to test.

class TestStandardOut(luna.test_case.TestCase):
	"""
	Tests the behaviour of the standard_out logger implementation.
	"""

	_test_messages = {
		"simple":    {"message": "Message.",                 "title": "Title"},
		"empty":     {"message": "",                         "title": ""},
		"multiline": {"message": "First line\nSecond line.", "title": "Multiline"},
		"unicode":   {"message": "\u263d",                   "title": "\u263e"}
	}
	"""
	Messages that every message logging test should test with.
	"""

	def setUp(self):
		"""
		Prepares for a test by intercepting the stdout channel.
		"""
		self._actual_stdout = sys.stdout
		self._mock_stdout = io.StringIO()
		sys.stdout = self._mock_stdout #Swaps out stdout with something that we can verify the contents of.

	def tearDown(self):
		"""
		Restores the state of the stdout channel after tests.
		"""
		sys.stdout = self._actual_stdout
		self._mock_stdout.close()

	@luna.test_case.parametrise(_test_messages)
	def test_critical(self, message, title):
		"""
		Tests printing a critical message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.critical(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

	@luna.test_case.parametrise(_test_messages)
	def test_info(self, message, title):
		"""
		Tests printing an information message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.info(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

if __name__ == "__main__":
	unittest.main()