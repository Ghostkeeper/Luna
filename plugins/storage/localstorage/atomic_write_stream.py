#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides an I/O stream that implements atomic writing to a file.

While streaming, the data gets written to a temporary file. When the stream is
closed, this temporary file gets moved over the target file.
"""

import os #To reconstruct the full path of the temporary file.
import tempfile #To create temporary files to write to and move them to the actual file location.

import localstorage.local_storage #For the move function.

class AtomicWriteStream:
	"""
	An I/O stream that implements atomic writing to a file on the local machine.

	While streaming, the data gets written to a temporary file. When the stream
	is closed, this temporary file gets moved over the target file. The move is
	an atomic operation on all supported operating systems, so the actual write
	also becomes atomic.

	Flushing this stream is not supported, as that prevents the write from being
	atomic.
	"""

	def __init__(self, path):
		"""
		Creates a new atomic write stream.

		This initialises the temporary file.
		:param path: The path of the actual file to write to (not the temporary
		file).
		"""
		self._directory, _ = os.path.split(path) #Put the temporary file in the same directory, so it will be on the same file system which guarantees an atomic move.
		self._temp_file = tempfile.NamedTemporaryFile(dir=self._directory, delete=False, mode="wb")
		self._target_path = path #Store for when we actually do the rename.

	def __enter__(self):
		"""
		Starts writing to the file.

		This command is simply passed on to the temporary file.

		:return: This AtomicWriteStream instance.
		"""
		self._temp_file.__enter__()
		return self #Need to override this because we want to return ourselves, not the NamedTemporaryFile instance.

	def __exit__(self, exception_type, exception_value, traceback):
		"""
		Stops writing to the file.

		When this happens, the temporary file is moved to the final destination.

		:param exception_type: The type of any exception thrown during the with
		block, or ``None`` if no exception was thrown.
		:param exception_value: An instance of the exception that was thrown
		during the with block, or ``None`` if no exception was thrown.
		:param traceback: The traceback of any exception that was thrown during
		the with block, or ``None`` if no exception was thrown.
		"""
		self._temp_file.flush() #Make sure it's all written.
		os.fsync(self._temp_file.fileno()) #Make sure that the file system is up-to-date.
		self._temp_file.__exit__(exception_type, exception_value, traceback)
		self.close()

	def __getattr__(self, name):
		"""
		Gets an attribute of the temporary file.

		This makes the stream behaves as if it wraps the temporary file.
		Normally it would be desirable to use inheritance instead, but the
		actual file stream in the ``tempfile`` module is not exposed.

		:param name: The name of the attribute to get from the temporary file
		stream.
		:return: The value of the attribute in the temporary file stream.
		"""
		return self._temp_file.__getattr__(name)

#Probably going to have to use __getattr__ to wrap around the temp stream.
#See https://github.com/python/cpython/blob/master/Lib/tempfile.py#L459

	def close(self):
		"""
		Closes the file for writing, finalising the write.
		"""
		localstorage.local_storage.move(os.path.join(self._directory, self._temp_file.name), self._target_path) #Move the new file into place, replacing the old file if it existed.

	def flush(self):
		"""
		Raises an exception that this operation is not supported.

		Flushing is not supported by this file stream for three reasons. First,
		it is inherently against atomic file writing, since it can be used to
		save incomplete buffers already in the file. Secondly, the storage API
		does not expose the functionality. And thirdly, though one could expect
		that the flush would atomically write the current buffer to the target
		file, this would be prohibitively expensive to perform since it requires
		making a new copy of the current buffer before moving the old buffer to
		the file, and the first operation takes linear time to the size of the
		file. Copying the file at every flush is too expensive.

		:raises BufferError: This operation is not supported.
		"""
		raise BufferError("This is a file stream that writes atomically, and can therefore not be flushed.")