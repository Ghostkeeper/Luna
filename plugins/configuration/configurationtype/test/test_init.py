#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validation function for configuration types.
"""

import functools #To test filling in partials via metadata.

import configurationtype #The module we're testing.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.tests #For parametrised tests

class IncompleteConfiguration:
	"""
	A mock class for a configuration type, except that it misses iteration.
	"""

	def __getitem__(self, *args, **kwargs):
		"""
		Gets a configuration element. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.

		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		"""
		raise AssertionError("An item was requested by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def deserialise(self, *args, **kwargs): #pylint: disable=no-self-use
		"""
		Sets the state of configuration to what is represented by a byte
		sequence. This raises an ``AssertionError``.

		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		"""
		raise AssertionError("The deserialise function was called by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def serialise(self, *args, **kwargs): #pylint: disable=no-self-use
		"""
		Serialises the state of configuration. This raises an
		``AssertionError``.

		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		"""
		raise AssertionError("The serialise function was called by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

class ValidConfiguration(IncompleteConfiguration):
	"""
	A mock class that is a valid implementation of a configuration instance.
	"""

	def __iter__(self, *args, **kwargs):
		"""
		Creates an iterator over the class. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.

		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		"""
		raise AssertionError("The iteration function was called by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

class TestConfigurationType(luna.tests.TestCase):
	"""
	Tests the behaviour of the validation function for configuration types.
	"""

	def test_validate_metadata_correct(self):
		"""
		Tests the ``validate_metadata`` function against metadata that is
		correct.
		"""
		configurationtype.validate_metadata({
			"configuration": {
				"name": "Test Configuration",
				"instance": ValidConfiguration()
			}
		}) #Should not give an exception.

	@luna.tests.parametrise({
		"no_configuration": {
			"metadata": {
				"something_else": {}
			}
		},
		"string": {
			"metadata": {
				"configuration": "not_a_dictionary"
			}
		},
		"integer": {
			"metadata": {
				"configuration": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"configuration": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"configuration": luna.tests.AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"configuration": {}
			}
		},
		"missing_name": {
			"metadata": {
				"instance": ValidConfiguration()
			}
		},
		"missing_instance": {
			"metadata": {
				"name": "Test Missing Instance"
			}
		},
		"name_not_string": {
			"metadata": {
				"name": 69,
				"instance": ValidConfiguration()
			}
		},
		"instance_none": {
			"metadata": {
				"name": "Test Instance None",
				"instance": None,
			}
		},
		"instance_str": {
			"metadata": {
				"name": "Test Instance String",
				"instance": "Some Text" #Missing __getitem__, deserialise and serialise methods.
			}
		},
		"instance_incomplete": {
			"metadata": {
				"name": "Test Instance Incomplete",
				"instance": IncompleteConfiguration() #Missing __iter__ method.
			}
		}
	})
	def test_validate_metadata_incorrect(self, metadata):
		"""
		Tests the ``validate_metadata`` function against metadata that is
		incorrect.

		The function is tested with various instances of metadata, all of which
		are incorrect. The test expects the function to raise a
		``MetadataValidationError``.

		:param metadata: Incorrect metadata.
		"""
		with self.assertRaises(luna.plugins.MetadataValidationError): #Should give this exception.
			configurationtype.validate_metadata(metadata)