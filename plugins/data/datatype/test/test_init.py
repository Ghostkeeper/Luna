#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the validation function for data types.
"""

import functools #To test filling in partials via metadata.

import datatype #The module we're testing.
import luna.plugins #To check whether a MetadataValidationError is raised.
import luna.tests #For parametrised tests.

class TestDataType(luna.tests.TestCase):
	"""
	Tests the behaviour of the validation function for data types.
	"""

	#pylint: disable=no-self-use
	@luna.tests.parametrise({
		"functions": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function
				}
			}
		},
		"various_callables": {
			"metadata": {
				"data": {
					"deserialise": print, #A built-in.
					"is_instance": luna.tests.CallableObject, #A callable object.
					"is_serialised": lambda x: x, #A lambda function.
					"serialise": functools.partial(luna.tests.arbitrary_function, 3) #A partial function.
				}
			}
		},
		"mime_type": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "type/test",
					"name": "Testing data"
				}
			}
		},
		"mime_type_extensions": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "type/test",
					"name": "Testing data",
					"extensions": {"tst", "log"}
				}
			}
		},
		"mime_type_extensions_empty": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "type/test",
					"name": "Testing data",
					"extensions": {}
				}
			}
		},
		"mime_type_specialchars": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "a..-_!#$^&9001/b",
					"name": "Testing data"
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
		datatype.validate_metadata(metadata) #Should not give an exception.

	@luna.tests.parametrise({
		"no_data": {
			"metadata": {
				"not_data": {}
			}
		},
		"string": {
			"metadata": {
				"data": "not_a_dictionary"
			}
		},
		"integer": {
			"metadata": {
				"data": 1337 #Even the "in" keyword won't work.
			}
		},
		"none": {
			"metadata": {
				"data": None
			}
		},
		"almost_dictionary": {
			"metadata": {
				"data": luna.tests.AlmostDictionary()
			}
		},
		"empty": {
			"metadata": {
				"data": {}
			}
		},
		"missing_is_serialised": { #Doesn't have the "is_serialised" function.
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
				}
			}
		},
		"not_callable": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": "This is not a callable object.",
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
				}
			}
		},
		"partial_mime": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "type/test",
					"extensions": {"tst"}
				}
			}
		},
		"partial_mime_extensions": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"extensions": {"tst"}
				}
			}
		},
		"wrong_mime_chars": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "$1million/dollars", #Not allowed to start with a special character.
					"name": "Testing data"
				}
			}
		},
		"no_mime_slash": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "image",
					"name": "Testing data"
				}
			}
		},
		"extensions_not_iterable": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "test/x-test",
					"name": "Test MIME Type",
					"extensions": -1 #Try counting to that!
				}
			}
		},
		"extensions_string": {
			"metadata": {
				"data": {
					"deserialise": luna.tests.arbitrary_function,
					"is_instance": luna.tests.arbitrary_function,
					"is_serialised": luna.tests.arbitrary_function,
					"serialise": luna.tests.arbitrary_function,
					"mime_type": "test/x-test",
					"name": "Test MIME Type",
					"extensions": "doc" #Must be a sequence, not a single extension.
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
			datatype.validate_metadata(metadata)