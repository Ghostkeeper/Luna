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
import luna.tests #For parametrised tests.

class TestLoggerType(luna.tests.TestCase):
	"""
	Tests the behaviour of the registration and validation functions for
	loggers.
	"""

	#pylint: disable=no-self-use
	@luna.tests.parametrise({
		"functions": {
			"metadata": {
				"logger": {
					"critical": luna.tests.arbitrary_function,
					"debug": luna.tests.arbitrary_function,
					"error": luna.tests.arbitrary_function,
					"info": luna.tests.arbitrary_function,
					"warning": luna.tests.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"logger": {
					"critical": print, #A built-in.
					"debug": luna.tests.TestCase.arbitrary_method, #A normal function.
					"error": luna.tests.CallableObject, #A callable object.
					"info": lambda x: x, #A lambda function.
					"warning": functools.partial(luna.tests.arbitrary_function, 3) #A partial function.
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

	@luna.tests.parametrise({
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
				"logger": luna.tests.AlmostDictionary()
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
					"critical": luna.tests.arbitrary_function,
					"debug": luna.tests.arbitrary_function,
					"error": luna.tests.arbitrary_function,
					"info": luna.tests.arbitrary_function
				}
			}
		},
		"not_callable": {
			"metadata": {
				"logger": {
					"critical": luna.tests.arbitrary_function,
					"debug": "This is not a callable object.",
					"error": luna.tests.arbitrary_function,
					"info": luna.tests.arbitrary_function,
					"warning": luna.tests.arbitrary_function
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