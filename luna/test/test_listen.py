#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the listening module that provides a way to listen for state changes.
"""

import unittest #To define automatic tests.
import unittest.mock #To track how often a listener function was called.
import weakref #To check whether objects are properly garbage collected.

import luna.listen #The module we're testing.
import luna.tests #To get an object that is not callable.

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

	def test_listen_dictionary_add(self):
		"""
		Tests listening for new items in a dictionary.
		"""
		dictionary = luna.listen.DictionaryModel()
		luna.listen.listen(self.listener, dictionary, "foo")
		dictionary["foo"] = "bar"
		self.listener.assert_called_once_with("foo", "bar")

	def test_listen_dictionary_remove(self):
		"""
		Tests listening for removed items in a dictionary.
		"""
		dictionary = luna.listen.DictionaryModel()
		dictionary["item"] = "Flask of Invincibility"
		luna.listen.listen(self.listener, dictionary, "item")
		del dictionary["item"]
		self.listener.assert_called_once_with("item", None)

	def test_listen_dictionary_set(self):
		"""
		Tests listening for changing items in a dictionary.
		"""
		dictionary = luna.listen.DictionaryModel()
		dictionary["pie"] = "delicious"
		luna.listen.listen(self.listener, dictionary, "pie")
		dictionary["pie"] = "eaten"
		self.listener.assert_called_once_with("pie", "eaten")

	def test_listen_future_attribute(self):
		"""
		Tests listening to attributes that don't exist yet.
		"""
		luna.listen.listen(self.listener, self, "field_float")
		self.field_float = 3.14 #pylint: disable=attribute-defined-outside-init
		self.listener.assert_called_with("field_float", 3.14)

	def test_listen_memory_leak(self):
		"""
		Tests whether the listener trackers properly don't prevent garbage
		collection from collecting the objects surrounding the listener.
		"""
		listener = luna.tests.AlmostDictionary()
		listener_ref = weakref.ref(listener) #If this references to None, the object is garbage collected.
		luna.listen.listen(listener, self, "field_integer")
		listener = None #Should delete the listener from memory.
		self.field_integer = 2
		self.assertIsNone(listener, "Just a check to prevent code optimisers from removing the deallocation of the listener.") #Setting the variable to None must be executed.
		self.assertIsNone(listener_ref(), "The listener must have been deallocated.")

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

	def test_listen_new_fields(self):
		"""
		Test listening to all changes of an instance and then making new fields.
		"""
		luna.listen.listen(self.listener, self)
		self.field_float = 3.1416 #pylint: disable=attribute-defined-outside-init
		self.listener.assert_called_once_with("field_float", 3.1416)

	def test_listen_no_change(self):
		"""
		Tests that the listener doesn't get called if the state doesn't change.
		"""
		luna.listen.listen(self.listener, self, "field_integer")
		self.field_integer = 0 #Equal to starting state.
		self.listener.assert_not_called()

	def test_listen_remove_field(self):
		"""
		Tests whether removing a field triggers the listeners of the field.
		"""
		self.field_float = 3.14 #pylint: disable=attribute-defined-outside-init
		luna.listen.listen(self.listener, self, "field_float")
		del self.field_float
		self.listener.assert_called_once_with("field_float", None)

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

	def test_listen_value_multiple_values(self):
		"""
		Tests listening for either of two values of the same attribute.
		"""
		luna.listen.listen_value(self.listener, self, "field_integer", 2)
		luna.listen.listen_value(self.listener, self, "field_integer", 4)
		self.field_integer = 1
		self.listener.assert_not_called()
		self.field_integer = 2
		self.listener.assert_called_once_with()
		self.field_integer = 3
		self.listener.assert_called_once_with()
		self.field_integer = 4
		self.listener.assert_called_with()
		self.assertEqual(self.listener.call_count, 2, "The listener must have been called twice, once for each possible value.")

	def test_listen_value_simple(self):
		"""
		Tests listening for a specific value.
		"""
		luna.listen.listen_value(self.listener, self, "field_integer", 3)
		self.field_integer = 1
		self.listener.assert_not_called()
		self.field_integer = 2
		self.listener.assert_not_called()
		self.field_integer = 3
		self.listener.assert_called_once_with()