#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validation and registration functions for
configuration types.
"""

import configurationtype #The module we're testing.
import configurationtype.configuration_error #To test whether ConfigurationError is raised.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.tests #For parametrised tests

class IncompleteConfiguration:
	"""
	A mock class for a configuration type, except that it misses iteration.
	"""

	def __getattr__(self, *args, **kwargs):
		"""
		Gets the value of a configuration item. This raises an
		``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("An item was requested by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def __setattr__(self, *args, **kwargs):
		"""
		Changes the value of a configuration item. This raises an
		``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("An item was set by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def _define(self, *args, **kwargs):
		"""
		Creates a new configuration item. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("A new item was defined by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def _load(self, *args, **kwargs): #pylint: disable=no-self-use
		"""
		Loads configuration from a directory. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("The _load function was called by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def _metadata(self, *args, **kwargs):
		"""
		Obtains the metadata of an item. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("Item metadata was requested by the plug-in metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

	def _save(self, *args, **kwargs): #pylint: disable=no-self-use
		"""
		Saves the state of configuration. This raises an ``AssertionError``.

		The metadata validator should never call any function on the instance.
		:param args: All arguments will be put in the exception's message.
		:param kwargs: All arguments will be put in the exception's message.
		:raises AssertionError: Always.
		"""
		raise AssertionError("The _save function was called by the metadata validator with parameters {args} and {kwargs}.".format(args=str(args), kwargs=str(kwargs)))

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
	Tests the behaviour of the validation and registration functions for
	configuration types.
	"""

	@luna.tests.parametrise({
		"define":      {"identity": "define"},
		"__getattr__": {"identity": "__getattr__"},
		"metadata":    {"identity": "metadata"}
	})
	def test_register_clashing(self, identity):
		"""
		Tests whether registering a plug-in with an identity that clashes
		results in a ``ConfigurationError``.

		Normally we'd want to test this by patching the configuration API with
		some class we made for this test, so that any changes to the API will
		not cause false negatives for this test. However, since ``dir()`` is not
		transparently patched through when using ``unittest.mock.patch()``, this
		is not a viable option this time. We'll have to settle with updating the
		test sometimes.
		:param identity: The identity of the plug-in to register.
		"""
		with self.assertRaises(configurationtype.configuration_error.ConfigurationError):
			configurationtype.register(identity, {})

	@luna.tests.parametrise({
		"preferences": {"identity": "preferences"},
		"with_digit0": {"identity": "with_digit0"}
	})
	def test_register_safe(self, identity):
		"""
		Tests whether registering a plug-in with a good identity works.
		:param identity: The identity of the plug-in to register.
		"""
		configurationtype.register(identity, {})

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