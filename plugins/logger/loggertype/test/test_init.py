#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the registration and validation functions for loggers.
"""

import functools #To test filling in partials via metadata.

import loggertype #The module we're testing.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.test_case #For parametrised tests.

class TestLoggerType(luna.test_case.TestCase):
	"""
	Tests the behaviour of the registration and validation functions for
	loggers.
	"""

	#pylint: disable=no-self-use
	@luna.test_case.parametrise({
		"functions": {
			"metadata": {
				"logger": {
					"critical": luna.test_case.arbitrary_function,
					"debug": luna.test_case.arbitrary_function,
					"error": luna.test_case.arbitrary_function,
					"info": luna.test_case.arbitrary_function,
					"warning": luna.test_case.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"logger": {
					"critical": print, #A built-in.
					"debug": luna.test_case.TestCase.arbitrary_method, #A normal function.
					"error": luna.test_case.CallableObject, #A callable object.
					"info": lambda x: x, #A lambda function.
					"warning": functools.partial(luna.test_case.arbitrary_function, 3) #A partial function.
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
		loggertype.validate_metadata(metadata) #Should not give an exception.

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
				"logger": luna.test_case.AlmostDictionary()
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
					"critical": luna.test_case.arbitrary_function,
					"debug": luna.test_case.arbitrary_function,
					"error": luna.test_case.arbitrary_function,
					"info": luna.test_case.arbitrary_function
				}
			}
		},
		"not_callable": {
			"metadata": {
				"logger": {
					"critical": luna.test_case.arbitrary_function,
					"debug": "This is not a callable object.",
					"error": luna.test_case.arbitrary_function,
					"info": luna.test_case.arbitrary_function,
					"warning": luna.test_case.arbitrary_function
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
			loggertype.validate_metadata(metadata)