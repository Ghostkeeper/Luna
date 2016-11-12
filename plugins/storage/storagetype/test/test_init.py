#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the registration and validation functions for storage.
"""

import functools #To test filling in partial functions via metadata.

import luna.plugins #To test if something raises MetadataValidationException.
import luna.test_case #To parametrise the tests.
import storagetype #The module we're testing.

def _arbitrary_function(*args, **kwargs):
	"""
	A function to provide in test metadata.

	Since the validation should never actually call functions, this function
	just raises a validation error.

	:param args: Positional arguments.
	:param kwargs: Key-word arguments.
	"""
	raise luna.plugins.MetadataValidationError("The metadata validation called a function of the API (with parameters {args} and key-word arguments {kwargs}).".format(args=args, kwargs=kwargs))

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

class TestInit(luna.test_case.TestCase):
	"""
	Tests the behaviour of the registration and validation functions for
	loggers.
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
				"storage": {
					"can_read": _arbitrary_function,
					"can_write": _arbitrary_function,
					"delete": _arbitrary_function,
					"exists": _arbitrary_function,
					"move": _arbitrary_function,
					"read": _arbitrary_function,
					"write": _arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"storage": {
					"can_read": print, #A built-in.
					"can_write": _arbitrary_method, #A normal method.
					"delete": _CallableObject, #A callable object.
					"exists": lambda x: x, #A lambda function.
					"move": functools.partial(_arbitrary_function, 3), #A partial function.
					"read": _arbitrary_function,
					"write": _arbitrary_function
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
		storagetype.validate_metadata(metadata) #Should not give an exception.

	@luna.test_case.parametrise({
		"no_storage": {
			"metadata": {
				"not_storage": {}
			}
		},
		"string": {
			"metadata": {
				"storage": "not_a_dictionary"
			}
		},
		"integer": {
			"metadata": {
				"storage": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"storage": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"storage": _AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"storage": {}
			}
		},
		"missing_write": { #Doesn't have the "write" function.
			"metadata": {
				"storage": {
					"can_read": _arbitrary_function,
					"can_write": _arbitrary_function,
					"delete": _arbitrary_function,
					"exists": _arbitrary_function,
					"read": _arbitrary_function,
					#"write" is missing.
				}
			}
		},
		"not_callable": {
			"metadata": {
				"storage": {
					"can_read": _arbitrary_function,
					"can_write": _arbitrary_function,
					"delete": "This is not a callable object.",
					"exists": _arbitrary_function,
					"read": _arbitrary_function,
					"write": _arbitrary_function
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
			storagetype.validate_metadata(metadata)