#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validation function for user interfaces.
"""

import luna.plugins #To test if something raises MetadataValidationException.
import luna.tests #To parametrise the tests.
import userinterfacetype #The module we're testing.

class TestInit(luna.tests.TestCase):
	"""
	Tests the behaviour of the validation function for user interfaces.
	"""

	#pylint: disable=no-self-use
	@luna.tests.parametrise({
		"functions": {
			"metadata": {
				"userinterface": {
					"join": luna.tests.arbitrary_function,
					"start": luna.tests.arbitrary_function,
					"stop": luna.tests.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"userinterface": {
					"join": luna.tests.CallableObject,
					"start": lambda x: x, #A lambda function.
					"stop": print #A built-in.
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
		userinterfacetype.validate_metadata(metadata) #Should not give an exception.

	@luna.tests.parametrise({
		"no_userinterface": {
			"metadata": {
				"not_userinterface": {}
			}
		},
		"string": {
			"metadata": {
				"userinterface": "not_a_dictionary"
			}
		},
		"integer": {
			"metadata": {
				"userinterface": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"userinterface": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"userinterface": luna.tests.AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"userinterface": {}
			}
		},
		"missing_start": { #Doesn't have the "start" function.
			"metadata": {
				"userinterface": {
					"join": luna.tests.arbitrary_function,
					#"start" is missing.
					"stop": luna.tests.arbitrary_function
				}
			}
		},
		"not_callable": {
			"metadata": {
				"userinterface": {
					"join": luna.tests.arbitrary_function,
					"start": luna.tests.arbitrary_function,
					"stop": "This is not a callable object."
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
			userinterfacetype.validate_metadata(metadata)