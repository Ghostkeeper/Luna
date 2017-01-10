#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
This module presents some classes that help with streaming data for
inter-component communication.
"""

import io #To use the standard I/O streams as helper.

class BytesStreamReader:
	"""
	A stream that wraps around a ``BufferedReader`` instance and allows
	iterating byte-by-byte.

	For the rest, the reader behaves exactly the same as ``BufferedReader``.
	Only iterating over it yields separate bytes.

	The built-in ``BufferedReader`` can read binary streams, but iterating over
	them still yields the data line-by-line. This is undesirable since lines
	typically have no meaning for binary files.
	"""

	def __init__(self, wrapped):
		"""
		Creates the ``BytesStreamReader``, wrapping it around the original
		stream.
		:param wrapped: The ``BufferedReader`` stream to wrap around.
		"""
		if type(wrapped) == bytes:
			wrapped = io.BytesIO(wrapped)
		self._wrapped = wrapped

	def __enter__(self):
		"""
		Starts reading from the stream.

		This command is simply passed on to the wrapped stream.
		:return: This BytesStreamReader instance.
		"""
		self._wrapped.__enter__()
		return self #Need to override this because we want to return ourselves, not the BufferedReader instance.

	def __exit__(self, exception_type, exception_value, traceback):
		"""
		Stops reading from the stream.
		:param exception_type: The type of any exception thrown during the
		``with`` block, or ``None`` if no exception was thrown.
		:param exception_value: An instance of the exception that was thrown
		during the ``with`` block, or ``None`` if no exception was thrown.
		:param traceback: The traceback of any exception that was thrown during
		the ``with`` block, or ``None`` if no exception was thrown.
		"""
		self._wrapped.__exit__()

	def __getattr__(self, item):
		"""
		Passes ordinary calls to the stream on to the wrapped
		``BufferedReader``.

		Only attributes that are defined in this class are not passed on.
		:param item: The attribute to get from ``BufferedReader``.
		:return:
		"""
		return getattr(self._wrapped, item)

	def __iter__(self):
		"""
		Creates an iterator that iterates over the bytes in this stream.

		This turns the ``BytesStreamReader`` into a ``bytes``-like class.
		:return: A sequence of bytes in the stream.
		"""
		for line in self._wrapped:
			yield from line