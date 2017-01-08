#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the enumerated type data type.

These tests are mostly interface-based, meaning that they will not test actual
output a lot, but tests the behaviour of the units instead.
"""

import enum #To define example enumerated types to test with.
import test.test_enum #Built-in enumerated types to test with.

import enumerated.enumerated_type #The module we're testing.
import luna.tests #For parametrised tests.

class Animal(enum.Enum):
	"""
	An example enumerated type to perform tests on.
	"""
	CAT = 0
	DOG = 1
	BIRD = 2

class EnumContainer:
	"""
	A class that contains a nested enum to test with.
	"""
	class Material(enum.Enum):
		"""
		A nested enumerated type inside another class.

		We test with this because it has a different import path if it is
		defined this way.
		"""
		IRON = 3
		STONE = 4
		WOOD = 5

class TestEnumeratedType(luna.tests.TestCase):
	"""
	Tests the behaviour of various functions belonging to the enumerated type.

	In particular, it focuses on how these functions interact and integrate with
	each other.
	"""

	@luna.tests.parametrise({
		"module_local": {
			"instance": Animal.CAT
		},
		"module_local2": { #Different module-local one that is not the first-defined entry.
			"instance": Animal.BIRD
		},
		"builtins": {
			"instance": test.test_enum.Fruit.tomato
		},
		"nested": {
			"instance": EnumContainer.Material.STONE
		}
	})
	def test_serialise(self, instance):
		"""
		Tests whether we can serialise enumerated types.

		:param instance: The enumerated type instance to serialise.
		"""
		result = enumerated.enumerated_type.serialise(instance)
		self.assertIsInstance(result, bytes, "The serialised enumerated type must be a byte sequence.")