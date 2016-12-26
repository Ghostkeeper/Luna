#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validation function for MIME plug-ins.
"""

import mimetype #The module we're testing.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.tests #For parametrised tests.

class TestMimeType(luna.tests.TestCase):
	"""
	Tests the behaviour of the registration and validation functions for MIME
	plug-ins.
	"""

	#pylint: disable=no-self-use
	@luna.tests.parametrise({
		"no_extensions": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"extensions": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"extensions": ["foo", "bar"],
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"empty_extensions": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"extensions": [],
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"can_read": luna.tests.TestCase.arbitrary_method, #A bound method.
					"read": luna.tests.CallableObject #A callable object.
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
		mimetype.validate_metadata(metadata) #Should not give an exception.

	@luna.tests.parametrise({
		"no_mime": {
			"metadata": {
				"not_mime": {}
			}
		},
		"string": {
			"metadata": {
				"mime": "not_a_mime"
			}
		},
		"integer": {
			"metadata": {
				"mime": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"mime": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"mime": luna.tests.AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"mime": {}
			}
		},
		"missing_read": { #Doesn't have the "read" function.
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"can_read": luna.tests.arbitrary_function
				}
			}
		},
		"missing_can_read": { #Doesn't have the "can_read" function.
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"missing_mimetype": { #Doesn't have a MIME type entry.
			"metadata": {
				"mime": {
					"name": "Test MIME Type",
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"missing_name": { #Doesn't have a human-readable name.
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"extensions_not_iterable": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"extensions": -1, #Try counting to that!
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"extensions_string": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"extensions": "doc", #Must be a sequence, not a single extension.
					"can_read": luna.tests.arbitrary_function,
					"read": luna.tests.arbitrary_function
				}
			}
		},
		"not_callable": {
			"metadata": {
				"mime": {
					"mimetype": "test/x-test",
					"name": "Test MIME Type",
					"can_read": "This is not a callable object.",
					"read": luna.tests.arbitrary_function
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
			mimetype.validate_metadata(metadata)