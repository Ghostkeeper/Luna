#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the registrar that registers logger plug-ins.
"""

import functools #To test filling in partials via metadata.

import loggertype.logger_registrar #The module we're testing.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.test_case #For parametrised tests.

def _arbitrary_function(x, y):
	"""
	A function to provide in test metadata.

	:param x: The first argument.
	:param y: The second argument.
	:return The product of the two arguments.
	"""
	return x * y

class _CallableObject:
	"""
	An object to provide in test metadata which has a __call__ function.
	"""
	def __call__(self, *args, **kwargs):
		"""
		Calls the callable object, which does nothing.

		:param args: Arguments to call the object with.
		:param kwargs: Key-word arguments to call the object with.
		"""
		pass

class _AlmostDictionary:
	"""
	This class looks a lot like a dictionary, but isn't.

	It has no element look-up. It is used to check how well the validator
	handles errors in case the argument just happens to have a ``keys`` method.
	In this case it quacks like a duck, and walks sorta like a duck, but has no
	duck-waggle, so to say.
	"""
	def keys(self):
		"""
		Pretends to return the keys of a dictionary.

		:return: A list of keys.
		"""
		return dir(self).keys()

class TestLoggerRegistrar(luna.test_case.TestCase):
	"""
	Tests the behaviour of the registrar that registers logger plug-ins.
	"""

	def _arbitrary_method(self):
		"""
		A method to provide in test metadata.
		"""
		pass

	#pylint: disable=no-self-use
	@luna.test_case.parametrise({
		"functions": {
			"metadata": {
				"logger": {
					"critical": _arbitrary_function,
					"debug": _arbitrary_function,
					"error": _arbitrary_function,
					"info": _arbitrary_function,
					"warning": _arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"logger": {
					"critical": print, #A built-in.
					"debug": _arbitrary_method, #A normal function.
					"error": _CallableObject, #A callable object.
					"info": lambda x: x, #A lambda function.
					"warning": functools.partial(_arbitrary_function, 3) #A partial function.
				}
			}
		}
	})
	def test_validate_metadata_correct(self, metadata):
		"""
		Tests the ``validate_metadata`` function against metadata that is
		correct.

		The function is tested with various instances of metadata, all of which
		are correct. It is tested if the validation deems the metadata correct
		also.

		:param metadata: Correct metadata.
		"""
		loggertype.logger_registrar.validate_metadata(metadata) #Should not give an exception.

	@luna.test_case.parametrise({
		"no_logger": {
			"metadata": {
				"not_a_logger": {}
			}
		},
		"string": {
			"metadata": {
				"logger": "not_a_dictionary"
			}
		},
		"integer": {
			"metadata": {
				"logger": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"logger": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"logger": _AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"logger": {}
			}
		},
		"missing_warning": { #Doesn't have the "warning" function.
			"metadata": {
				"logger": {
					"critical": _arbitrary_function,
					"debug": _arbitrary_function,
					"error": _arbitrary_function,
					"info": _arbitrary_function
				}
			}
		},
		"not_callable": {
			"metadata": {
				"logger": {
					"critical": _arbitrary_function,
					"debug": "This is not a callable object.",
					"error": _arbitrary_function,
					"info": _arbitrary_function,
					"warning": _arbitrary_function
				}
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
			loggertype.logger_registrar.validate_metadata(metadata)