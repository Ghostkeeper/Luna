#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Defines helpers for writing tests.

Some of this logic is specific to Luna with its plug-in structure. The rest
could have been imported from a more sophisticated third-party unit testing
package. But as long as these features are small and few, we should not
introduce an external dependency.
"""

import functools #For partial functions and wrapper functions.
import unittest #For unittest's test case, which we extend.

class _TestCaseMeta(type):
	"""
	Metaclass to capture all parametrised tests and duplicate them for each of
	their parameter sets.
	"""

	def __new__(mcs, name, bases, members):
		"""
		Defines a new TestCase class.

		This intercepts all tests that are parametrised and duplicates them for
		each of the sets of parameters they need to be called with.
		:param name: The name of the TestCase class.
		:param bases: The superclasses of the TestCase class.
		:param members: The members of the TestCase class, including functions.
		:return: A new TestCase class, modified for parametrised tests.
		"""
		members_copy = dict(members)
		for member in members_copy:
			if callable(members_copy[member]) and hasattr(members_copy[member], "parameters"): #It's a function that's marked with the @parametrise annotation.
				for test_name, parameters in members_copy[member].parameters.items(): #Copy the function for each set of parameters.
					new_function = functools.partialmethod(members_copy[member], **parameters) #Fill in only the parameters. The rest is filled in at calling (such as "self").
					members[member + "_" + test_name] = new_function #Store the filled-in function along with the test name to make it unique.
				del members[member] #Delete the original parametrised function.
		return type.__new__(mcs, name, bases, members)

class TestCase(unittest.TestCase, metaclass=_TestCaseMeta):
	"""
	Extension of ``unittest.TestCase`` that adds all features that Luna's test
	cases need.
	"""

	def arbitrary_method(self, *args, **kwargs): #pylint: disable=no-self-use
		"""
		A bound method to test functional input with.

		The method should not be called by the test. Calling the method raises
		an ``AssertionError`` to indicate that the test failed.

		:param args: Positional arguments.
		:param kwargs: Key-word arguments.
		"""
		raise AssertionError("The arbitrary method was called by the test with parameters {args} and key-word arguments {kwargs}.".format(args=args, kwargs=kwargs))

def parametrise(parameters):
	"""
	Causes a test to run multiple times with different parameters.

	This only works for functions inside a `TestCase` class.

	:param parameters: A dictionary containing individual tests. The keys in the
		dictionary act as a name for the test, which is appended to the function
		name. The values of the dictionary are dictionaries themselves. These
		act as the parameters that are filled into the function.
	:return: A parametrised test case.
	"""
	def parametrise_decorator(original_function):
		"""
		Adds the parameters with which the test must be run to the function.

		:param original_function: The function to parametrise.
		:return: A function with the parameters attached.
		"""
		original_function.parameters = parameters
		return original_function
	return parametrise_decorator

def arbitrary_function(*args, **kwargs):
	"""
	A function to test functional input with.

	The function should not be called by the test. Calling the function raises
	an ``AssertionError`` to indicate that the test failed.

	:param args: Positional arguments.
	:param kwargs: Key-word arguments.
	"""
	raise AssertionError("The arbitrary function was called by the test with parameters {args} and key-word arguments {kwargs}.".format(args=args, kwargs=kwargs))

class CallableObject:
	"""
	An object to test functional input with. It has a __call__ function.
	"""
	def __call__(self, *args, **kwargs):
		"""
		Calls the callable object. This raises an ``AssertionError``.

		The object should not be called by the test. Calling the object raises
		an ``AssertionError`` to indicate that the test failed.

		:param args: Arguments to call the object with.
		:param kwargs: Key-word arguments to call the object with.
		"""
		raise AssertionError("The callable object was called by the test with parameters {args} and key-word arguments {kwargs}.".format(args=args, kwargs=kwargs))

class AlmostDictionary:
	"""
	This class looks a lot like a dictionary, but isn't.

	It has no element look-up. It can be used to check how well the a tested
	subject handles errors in case the argument just happens to have a ``keys``
	method. In this case it quacks like a duck, and walks sorta like a duck, but
	has no duck-waggle, so to say.
	"""
	def keys(self):
		"""
		Pretends to return the keys of a dictionary.

		:return: A list of strings that look like the keys of the dictionary.
		"""
		return dir(self).keys()