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

class TestInit(luna.test_case.TestCase):
	"""
	Tests the behaviour of the registration and validation functions for
	loggers.
	"""

	#pylint: disable=no-self-use
	@luna.test_case.parametrise({
		"functions": {
			"metadata": {
				"storage": {
					"can_read": luna.test_case.arbitrary_function,
					"can_write": luna.test_case.arbitrary_function,
					"delete": luna.test_case.arbitrary_function,
					"exists": luna.test_case.arbitrary_function,
					"move": luna.test_case.arbitrary_function,
					"read": luna.test_case.arbitrary_function,
					"write": luna.test_case.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"storage": {
					"can_read": print, #A built-in.
					"can_write": luna.test_case.TestCase.arbitrary_method, #A normal method.
					"delete": luna.test_case.CallableObject, #A callable object.
					"exists": lambda x: x, #A lambda function.
					"move": functools.partial(luna.test_case.arbitrary_function, 3), #A partial function.
					"read": luna.test_case.arbitrary_function,
					"write": luna.test_case.arbitrary_function
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
				"storage": luna.test_case.AlmostDictionary()
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
					"can_read": luna.test_case.arbitrary_function,
					"can_write": luna.test_case.arbitrary_function,
					"delete": luna.test_case.arbitrary_function,
					"exists": luna.test_case.arbitrary_function,
					"read": luna.test_case.arbitrary_function,
					#"write" is missing.
				}
			}
		},
		"not_callable": {
			"metadata": {
				"storage": {
					"can_read": luna.test_case.arbitrary_function,
					"can_write": luna.test_case.arbitrary_function,
					"delete": "This is not a callable object.",
					"exists": luna.test_case.arbitrary_function,
					"read": luna.test_case.arbitrary_function,
					"write": luna.test_case.arbitrary_function
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