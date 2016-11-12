#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the standard_out logger implementation.
"""

import io #Provides a replacement I/O channel to mock stdout.
import sys #To capture stdout.

import luna.tests #To get parametrised tests.
import standardout.standard_out #The module to test.

class TestStandardOut(luna.tests.TestCase):
	"""
	Tests the behaviour of the standard_out logger implementation.
	"""

	_test_messages = {
		"simple":    {"message": "Message.",                 "title": "Title"}, #pylint: disable=bad-whitespace
		"empty":     {"message": "",                         "title": ""}, #pylint: disable=bad-whitespace
		"multiline": {"message": "First line\nSecond line.", "title": "Multiline"},
		"unicode":   {"message": "\u263d",                   "title": "\u263e"} #pylint: disable=bad-whitespace
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

	@luna.tests.parametrise(_test_messages)
	def test_critical(self, message, title):
		"""
		Tests printing a critical message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.critical(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

	@luna.tests.parametrise(_test_messages)
	def test_debug(self, message, title):
		"""
		Tests printing a debug message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.debug(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

	@luna.tests.parametrise(_test_messages)
	def test_error(self, message, title):
		"""
		Tests printing an error message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.error(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

	@luna.tests.parametrise(_test_messages)
	def test_info(self, message, title):
		"""
		Tests printing an information message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.info(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

	def test_multiple_messages(self):
		"""
		Tests printing multiple messages after each other.

		It tests whether all messages are present and in correct order.
		"""
		standardout.standard_out.info("First")
		standardout.standard_out.error("Second")
		standardout.standard_out.info("Third")
		buffer_state = self._mock_stdout.getvalue()
		first_position = buffer_state.find("First")
		second_position = buffer_state.find("Second")
		third_position = buffer_state.find("Third")
		self.assertGreaterEqual(first_position, 0, msg="The first message is not in the log.")
		self.assertGreaterEqual(second_position, 0, msg="The second message is not in the log.")
		self.assertGreaterEqual(third_position, 0, msg="The third message is not in the log.")
		self.assertGreater(second_position, first_position, msg="The second message comes before the first message.")
		self.assertGreater(third_position, second_position, msg="The third message comes before the second message.")

	@luna.tests.parametrise(_test_messages)
	def test_warning(self, message, title):
		"""
		Tests printing a warning message.

		:param message: The message to print.
		:param title: The title to give the message.
		"""
		standardout.standard_out.warning(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())