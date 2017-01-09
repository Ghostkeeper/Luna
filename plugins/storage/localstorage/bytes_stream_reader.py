#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
A stream that reads bytes from a `BufferedReader` instance and allows iterating
byte-by-byte.

The built-in `BufferedReader` can read binary streams, but iterating over them
still yields the data line-by-line. This is undesirable since lines typically
have no meaning for binary files. This module presents a class that yields bytes
in that case, but otherwise behaves the same.
"""

class BytesStreamReader:
	"""
	A wrapper around a `BufferedReader` object that yields individual bytes when
	iterating over it.

	For the rest, the reader behaves exactly the same as `BufferedReader`. Only
	iterating over it yields separate bytes.
	"""

	def __init__(self, wrapped):
		"""
		Creates the `BytesStreamReader`, wrapping it around the original stream.
		:param wrapped: The `BufferedReader` stream to wrap around.
		"""
		self._wrapped = wrapped

	def __getattr__(self, item):
		"""
		Passes ordinary calls to the stream on to the wrapped `BufferedReader`.

		Only attributes that are defined in this class are not passed on.
		:param item: The attribute to get from `BufferedReader`.
		:return:
		"""
		return getattr(self._wrapped, item)

	def __iter__(self):
		"""
		Creates an iterator that iterates over the bytes in this stream.

		This turns the `BytesStreamReader` into a `bytes`-like class.
		:return: A sequence of bytes in the stream.
		"""
		for line in self._wrapped:
			yield from line