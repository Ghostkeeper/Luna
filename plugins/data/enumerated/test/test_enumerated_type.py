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
import io #To simulate a byte stream.
import test.test_enum #Built-in enumerated types to test with.
import unittest.mock #To replace the dependency on the data module.

import enumerated.enumerated_type #The module we're testing.
import luna.tests #For parametrised tests and mock exceptions.

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

def mock_api(plugin_type):
	"""
	Mocks calls to different APIs.

	This allows the tests to remain unit tests, even if the actual units try to
	call upon different plug-ins.
	:param plugin_type: The type of plug-in to mock.
	:return: A fake API for that plug-in.
	"""
	mock = unittest.mock.MagicMock()
	if plugin_type == "data": #We need to specify the SerialisationException as an actual exception since the "raise" keyword is not Pythonic: It actually tests for type!
		mock.SerialisationException = luna.tests.MockException
	return mock

class TestEnumeratedType(luna.tests.TestCase):
	"""
	Tests the behaviour of various functions belonging to the enumerated type.

	In particular, it focuses on how these functions interact and integrate with
	each other.
	"""
	#Ignore multiple spaces after assignment. It's used for outlining, dumb linter.
	#pylint: disable=C0326

	@luna.tests.parametrise({
		"custom":   {"serialised": b"enumerated.test.test_enumerated_type.Animal.CAT"},
		"custom2":  {"serialised": b"enumerated.test.test_enumerated_type.Animal.BIRD"},
		"builtins": {"serialised": b"test.test_enum.Fruit.tomato"},
		"nested":   {"serialised": b"enumerated.test.test_enumerated_type.EnumContainer.Material.STONE"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise(self, serialised):
		"""
		Tests whether we can deserialise enumerated types.
		:param serialised: The serialised form of some enumerated type.
		"""
		result = enumerated.enumerated_type.deserialise(io.BytesIO(serialised))
		self.assertIsInstance(result, enum.Enum)

	@luna.tests.parametrise({
		"not_utf_8":           {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"unknown_module":      {"serialised": b"evilcorp.destroy_the_world.VirusType.RANSOMWARE"}, #evilcorp does not exist.
		"unknown_submodule":   {"serialised": b"enumerated.test_oops_i_made_a_typo.test_enumerated_type.Animal.DOG"}, #test_oops_i_made_a_typo does not exist.
		"unknown_enum":        {"serialised": b"enumerated.test.test_enumerated_type.Colour.RED"}, #Colour does not exist.
		"unknown_instance":    {"serialised": b"enumerated.test.test_enumerated_type.Animal.SNAKE"}, #SNAKE does not exist.
		"unknown_subenum":     {"serialised": b"enumerated.test.test_enumerated_type.EnumContainer.Flower.ROSE"}, #Flower does not exist.
		"unknown_subinstance": {"serialised": b"enumerated.test.test_enumerated_type.EnumContainer.Material.GLASS"} #GLASS does not exist.
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_error(self, serialised):
		"""
		Tests fail cases in which the deserialisation must raise an exception.
		:param serialised: Some serialised data that is not an enumeration.
		"""
		with self.assertRaises(luna.tests.MockException):
			enumerated.enumerated_type.deserialise(io.BytesIO(serialised))

	@luna.tests.parametrise({
		"custom":   {"serialised": b"enumerated.test.test_enumerated_type.Animal.CAT"},
		"custom2":  {"serialised": b"enumerated.test.test_enumerated_type.Animal.BIRD"},
		"builtins": {"serialised": b"test.test_enum.Fruit.tomato"},
		"nested":   {"serialised": b"enumerated.test.test_enumerated_type.EnumContainer.Material.STONE"}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_deserialise_serialise(self, serialised):
		"""
		Tests whether deserialising and then serialising results in the same
		instance.
		:param serialised: The serialised form to start (and hopefully end up)
		with.
		"""
		instance = enumerated.enumerated_type.deserialise(io.BytesIO(serialised))
		new_serialised = enumerated.enumerated_type.serialise(instance)
		self.assertEqual(serialised, new_serialised, "The serialised form must be consistent after deserialising and serialising.")

	@luna.tests.parametrise({
		"empty":              {"serialised": b""},
		"single_piece":       {"serialised": b"Class"},
		"invalid_start":      {"serialised": b"1Class.INSTANCE"},
		"invalid_second":     {"serialised": b"Class.2INSTANCE"},
		"empty_piece":        {"serialised": b"module..Class.INSTANCE"}, #There are two dots between "module" and "Class".
		"not_utf_8":          {"serialised": bytes([0x80, 0x61, 0x62, 0x63])}, #First 0x80, the Euro sign, which is not an allowed start character for UTF-8. Then followed by "abc".
		"disallowed_char":    {"serialised": b"You.Are(Not).Alone"},
		"disallowed_start":   {"serialised": b"You.Are.(Not).Alone"},
		"dash":               {"serialised": b"Thats.some.weird-ass.class.NAME"},
		"spaces":             {"serialised": b"Listening to Two Steps From Hell right now"},
		"end_dot":            {"serialised": b"module.Class."},
		"special_start":      {"serialised": "module.Class.４evah".encode("utf_8")},
		"special_disallowed": {"serialised": "smilies.Cost.LIVES☠".encode("utf_8")}
	})
	def test_is_not_serialised(self, serialised):
		"""
		Tests whether bytes streams that don't represent enumerated types are
		identified as such.
		:param serialised: A sequence of bytes that doesn't represent an
		enumerated type.
		"""
		self.assertFalse(enumerated.enumerated_type.is_serialised(io.BytesIO(serialised)), "This must not be identified as a serialised enumerated type.")

	@luna.tests.parametrise({
		"simple": {"serialised": b"Type.INSTANCE"},
		"long": {"serialised": b"module.submodule.Class.Subclass.Type.INSTANCE"},
		"special_chars": {"serialised": "number7._under_score.middle·dot.punct﹍４bu".encode("utf_8")},
		"single_chars": {"serialised": b"a.b.C.d.E.f"},
		"alphabets": {"serialised": "Aa.ŇţȕʭπҎԴחڛܔނइকગଅஇఈఈഈഈฒກཀလႴᄍሐᎰᐄᚄᚭកᡳᥕᦆᴆᴷᵣᵦᵶᶢḆὩℝℋⅦⅷⰁⲘⴓⴵⶵ〥るルㄥㅂㆯ㐔ꀎ가更ﬀﭚﶩＤｱ".encode("utf_8")}
	})
	def test_is_serialised(self, serialised):
		"""
		Tests whether serialised forms of enumerated types are correctly
		identified as such.
		:param serialised: A correct serialised form of an enumerated type.
		"""
		self.assertTrue(enumerated.enumerated_type.is_serialised(io.BytesIO(serialised)), "This must be identified as a serialised enumerated type.")

	@luna.tests.parametrise({
		"module_local":  {"instance": Animal.CAT},
		"module_local2": {"instance": Animal.BIRD}, #Different module-local one that is not the first-defined entry.
		"builtins":      {"instance": test.test_enum.Fruit.tomato},
		"nested":        {"instance": EnumContainer.Material.STONE}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise(self, instance):
		"""
		Tests whether we can serialise enumerated types.
		:param instance: The enumerated type instance to serialise.
		"""
		result = enumerated.enumerated_type.serialise(instance)
		self.assertIsInstance(result, bytes, "The serialised enumerated type must be a byte sequence.")

	@luna.tests.parametrise({
		"module_local":  {"instance": Animal.CAT},
		"module_local2": {"instance": Animal.BIRD}, #Different module-local one that is not the first-defined entry.
		"builtins":      {"instance": test.test_enum.Fruit.tomato},
		"nested":        {"instance": EnumContainer.Material.STONE}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_deserialise(self, instance):
		"""
		Tests whether serialising and then deserialising results in the original
		instance.
		:param instance: The instance to start (and hopefully end up) with.
		"""
		serialised = enumerated.enumerated_type.serialise(instance)
		deserialised = enumerated.enumerated_type.deserialise(io.BytesIO(serialised))
		self.assertEqual(instance, deserialised, "The enumerated type must be the same after serialising and deserialising.")

	@luna.tests.parametrise({
		"integer":       {"instance": 3},
		"custom_object": {"instance": EnumContainer()}
	})
	@unittest.mock.patch("luna.plugins.api", mock_api)
	def test_serialise_error(self, instance):
		"""
		Tests fail cases in which serialisation must raise an exception.
		:param instance: An object that is not an enumerated type.
		"""
		with self.assertRaises(luna.tests.MockException):
			enumerated.enumerated_type.serialise(instance)