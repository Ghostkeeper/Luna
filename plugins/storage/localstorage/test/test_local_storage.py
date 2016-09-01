#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Tests the behaviour of the local_storage storage implementation.

Note that this test suite is meant to also test the behaviour of concurrent
operations to the file system. This requires actual file writes. This sort of
thing is very dependent on the operating system the tests are run on, and the
atomicity of operations even more so. The concurrency tests should therefore be
assumed to only hold for the operating system that the tests are running on.
"""

import functools #For partialmethod, to wrap arbitrary method calls with the __getattr__ function.
import unittest.mock #To replace file reading/writing with something that simulates external influence.
import os #Cleaning up test files afterwards, and getting file size to design a good test.

import luna.test_case #To get parametrised tests.
import localstorage.local_storage #The module we're testing.

_unsafe_target_file = "test.txt"
"""
A file that is being used by multiple threads at a time, in a simulation.

The mock functions simulate file I/O being applied to this file concurrently
with the actual operation. Interaction with this file is considered
thread-unsafe. Interaction with other files is considered thread-safe, and
should only be done in tests as long as it can be (almost) guaranteed that
no other process will interfere with the file.
"""

_concurrent_write_bytes_written = 0
"""
How many bytes the concurrent writing mock has written so far.

It writes up to 10 bytes.
"""

_original_open = open
"""
The original open function that opens a file normally.

This is stored to write normally to a file within the ``ConcurrentIOWrapper``,
even if the ``open`` function is patched to return a ``ConcurrentIOWrapper``
instead of its normal behaviour.
"""

class ConcurrentIOWrapper:
	"""
	Simulates concurrent writes to the I/O stream being wrapped.
	"""

	_written_bytes = 0
	"""
	How many bytes are written in this test.

	Stop writing if the whole string is written. This allows algorithms that are
	not wait-free to still pass the test.
	"""

	def __init__(self, stream, write_string):
		"""
		Creates a new I/O wrapper around a specified stream.

		All calls to this wrapper are passed on to the stream, but during this
		time, some other streams are passed on to the
		:param stream: The stream to wrap around.
		:param write_string: A string of characters to write during I/O
			operations with the stream. Note that this string is always written
			to the unsafe file, which is not necessarily the file for this
			stream.
		"""
		self._stream = stream
		self._write_string = write_string

	def __getattr__(self, item):
		"""
		Writes data to the concurrent stream, gets an attribute from the actual
		stream, then writes more data to the concurrent stream.

		:param item: The name of the attribute to get.
		:return: The value of the requested attribute.
		"""
		if hasattr(self._stream.__getattribute__(item), "__self__"): #Only catch method calls.
			if item == "read": #Catch ``read`` with a special function that also interjects halfway.
				return self._concurrent_write_and_read
			else:
				return functools.partial(self._concurrent_write_and_call, self._stream.__getattribute__(item))
		else:
			return self._stream.__getattribute__(item)

	def __enter__(self, *args, **kwargs):
		"""
		Enters the scope of the I/O stream.

		:param args: Positional arguments to pass to the I/O stream.
		:param kwargs: Key-word arguments to pass to the I/O stream.
		:return: The wrapping I/O stream.
		"""
		self._stream.__enter__(*args, **kwargs) #Return self instead of the stream's enter result, so I/O operations inside a with-clause happen on the wrapper.
		return self

	def __exit__(self, *args, **kwargs):
		"""
		Exits the scope of the I/O stream.

		This needs to exist for the with-clause to allow being called on the
		wrapper. It is a completely transparent wrapper around the actual I/O
		stream.

		:param args: Positional arguments to pass to the I/O stream.
		:param kwargs: Key-word arguments to pass to the I/O stream.
		:return: The result of exiting the I/O stream's scope.
		"""
		return self._stream.__exit__(*args, **kwargs)

	def _concurrent_write_and_call(self, function, *args, **kwargs):
		"""
		Calls a function, but concurrently writes to the unsafe target file.

		A byte is written to the unsafe target file before and after a function
		call.

		:param function: The function to call.
		:param args: The positional arguments to call the function with.
		:param kwargs: The key-word arguments to call the function with.
		:return: The result of the function call.
		"""
		if ConcurrentIOWrapper._written_bytes == 0: #The first time, completely overwrite the original file.
			with _original_open(_unsafe_target_file, "wb", buffering=0) as concurrent_handle:
				concurrent_handle.write(b"") #Clear the file.
		if ConcurrentIOWrapper._written_bytes < len(self._write_string): #Append one byte.
			with _original_open(_unsafe_target_file, "ab", buffering=0) as concurrent_handle:
				concurrent_handle.write(self._write_string[ConcurrentIOWrapper._written_bytes:ConcurrentIOWrapper._written_bytes + 1])
				ConcurrentIOWrapper._written_bytes += 1
		result = function(*args, **kwargs) #The actual call in between.
		if ConcurrentIOWrapper._written_bytes < len(self._write_string): #Append one byte again.
			with _original_open(_unsafe_target_file, "ab", buffering=0) as concurrent_handle:
				concurrent_handle.write(self._write_string[ConcurrentIOWrapper._written_bytes:ConcurrentIOWrapper._written_bytes + 1])
				ConcurrentIOWrapper._written_bytes += 1
		return result

	def _concurrent_write_and_read(self, *args, **kwargs):
		"""
		Calls the ``read`` function twice and inserts a concurrent write in
		between.

		:param args: The positional arguments passed to the ``read`` function.
		:param kwargs: The key-word arguments passed to the ``read`` function.
		:return: The result of the ``read`` function.
		"""
		if ConcurrentIOWrapper._written_bytes < len(self._write_string):
			#TODO: Wait for a while, equal to the minimum resolution of the file modification time stamp of the current file system. This prevents testing the non-atomic case of the current read implementation.
			first_part = self._stream.read(1) #If this fails, the file is empty. That is really a wrong way to test read atomicity with.
			if ConcurrentIOWrapper._written_bytes < len(self._write_string): #Append one byte.
				if ConcurrentIOWrapper._written_bytes == 0: #The first time, completely overwrite the original file.
					with _original_open(_unsafe_target_file, "wb", buffering=0) as concurrent_handle:
						concurrent_handle.write(b"") #Clear the file.
				with _original_open(_unsafe_target_file, "ab", buffering=0) as concurrent_handle:
					concurrent_handle.write(self._write_string[ConcurrentIOWrapper._written_bytes:ConcurrentIOWrapper._written_bytes + 1])
					ConcurrentIOWrapper._written_bytes += 1
			second_part = self._stream.read(*args, **kwargs) #Read the rest of the file.
			return first_part + second_part
		else: #Don't do the concurrent write. After some amount of calls the "writing" is done. We assume that there comes a time where this is the case in real situations.
			return self._stream.read(*args, **kwargs)

def _open_simulate_concurrency(file, *args, **kwargs):
	"""
	Opens a file, but simulates concurrent reads/writes to some files.

	The call to ``open`` is made transparently, but the resulting I/O stream is
	wrapped around by a class that is completely transparent, except that it
	writes data to the unsafe target file each time you call a method. This
	simulates concurrent writes to the file.

	The arguments and key-word arguments are explicitly not specified in this
	function, as they must be translucent towards the real ``open`` function,
	even when the real ``open`` function changes.

	:param file: The path to the file to open.
	:param args: Any additional arguments supplied to the open function.
	:param kwargs: Any additional key-word arguments supplied to the open
		function.
	:return: A wrapped IO stream that simulates concurrent writes to the
	"""
	if len(args) >= 2:
		args_list = list(args)
		args_list[1] = 0 #Change the "buffering" parameter.
		args = tuple(args_list)
		original_io_stream = _original_open(file, *args, **kwargs)
	else: #Provide our own "buffering" parameter.
		if "buffering" in kwargs:
			del kwargs["buffering"]
		original_io_stream = _original_open(file, buffering=0, *args, **kwargs)
	return ConcurrentIOWrapper(original_io_stream, b"1234567890")

class TestLocalStorage(luna.test_case.TestCase):
	"""
	Tests the behaviour of the local_storage storage implementation.
	"""

	_bad_uris = {
		"http": {
			"uri": "http://www.example.com/file.txt"
		},
		"empty": {
			"uri": ""
		},
		"parse error": {
			"uri": "http://[invalid/file.txt"
		}
	}

	_good_uris = {
		"unix file": {
			"uri": "file:///home/username/file.txt"
		},
		"windows file": {
			"uri": "file://C:/Users/username/file.txt"
		},
		"windows network file": {
			"uri": "file://server/file.txt"
		}
	}

	def setUp(self):
		"""
		Resets the number of bytes written concurrently in this test.
		"""
		ConcurrentIOWrapper._written_bytes = 0

	def tearDown(self):
		"""
		Removes any files that may have been written during these tests.
		"""
		if os.path.isfile(_unsafe_target_file):
			os.remove(_unsafe_target_file)

	@luna.test_case.parametrise(_good_uris)
	def test_can_read(self, uri):
		"""
		Tests whether the plug-in says it can read files that it should be able
		to read.

		:param uri: A URI of a file that the local storage plug-in should be
		able to read.
		"""
		self.assertTrue(localstorage.local_storage.can_read(uri))

	@luna.test_case.parametrise(_good_uris)
	def test_can_write(self, uri):
		"""
		Tests whether the plug-in says it can write files that it should be able
		to write.

		:param uri: A URI of a file that the local storage plug-in should be
		able to write.
		"""
		self.assertTrue(localstorage.local_storage.can_write(uri))

	@luna.test_case.parametrise(_bad_uris)
	def test_cannot_read(self, uri):
		"""
		Tests whether the plug-in says it cannot read files that it should not
		be able to read.

		:param uri: A URI of a resource that the local storage plug-in should
		not be able to read.
		"""
		self.assertFalse(localstorage.local_storage.can_read(uri))

	@luna.test_case.parametrise(_bad_uris)
	def test_cannot_write(self, uri):
		"""
		Tests whether the plug-in says it cannot write files that it should not
		be able to write.

		:param uri: A URI of a resource that the local storage plug-in should
		not be able to write.
		"""
		self.assertFalse(localstorage.local_storage.can_write(uri))

	def test_exists_after_deleting(self):
		"""
		Tests whether a file is said to exist if it was just deleted.
		"""
		with open(_unsafe_target_file, "w") as file_handle: #Create the file.
			file_handle.write("Test!")
		os.remove(_unsafe_target_file) #Delete it.
		self.assertFalse(localstorage.local_storage.exists(_unsafe_target_file), msg="The file {file_name} was reported to exist, but it was just deleted.".format(file_name=_unsafe_target_file))

	def test_exists_just_created(self):
		"""
		Tests whether a file is said to exist if it has just been created.
		"""
		with open(_unsafe_target_file, "w") as file_handle: #Create the file.
			file_handle.write("Test!")
		self.assertTrue(localstorage.local_storage.exists(_unsafe_target_file), msg="The file {file_name} was reported to not exist, but it was just created.".format(file_name=_unsafe_target_file))

	def test_exists_never_created(self):
		"""
		Tests whether a file is said to not exist if it was never created.
		"""
		self.assertFalse(localstorage.local_storage.exists(_unsafe_target_file), msg="The file {file_name} was reported to be existing, though it shouldn't exist.".format(file_name=_unsafe_target_file)) #If stuff was cleaned up properly after each test, this should not exist.

	def test_read_atomicity(self):
		"""
		Tests the read function to see whether it is an atomic read.
		"""
		with open(_unsafe_target_file, "wb") as unsafe_file_handle:
			unsafe_file_handle.write(b"Test") #Some initial data to test with. This is not tested.

		with unittest.mock.patch("builtins.open", _open_simulate_concurrency):
			result = localstorage.local_storage.read(_unsafe_target_file)
			self.assertIn(result, [ #At any stage during the writing.
				b"Test",
				b"1",
				b"12",
				b"123",
				b"1234",
				b"12345",
				b"123456",
				b"1234567",
				b"12345678",
				b"123456789",
				b"1234567890"
			], result.decode("utf-8") + " is not a snapshot of the file at any point in time, and as such is not atomic.")

	def test_write_atomicity(self):
		"""
		Tests the write function to see whether it is an atomic write.
		"""
		test_bytes = b"Test"
		with unittest.mock.patch("builtins.open", _open_simulate_concurrency):
			localstorage.local_storage.write(_unsafe_target_file, test_bytes)
		with open(_unsafe_target_file, "rb") as written_file_handle:
			result = written_file_handle.read()
			self.assertEqual(result, test_bytes, "File write is not atomic.")