#!/usr/bin/env python

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
#software, either in source code form or as a compiled binary, for any purpose,
#commercial or non-commercial, and by any means.
#
#In jurisdictions that recognise copyright laws, the author or authors of this
#software dedicate any and all copyright interest in the software to the public
#domain. We make this dedication for the benefit of the public at large and to
#the detriment of our heirs and successors. We intend this dedication to be an
#overt act of relinquishment in perpetuity of all present and future rights to
#this software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <https://unlicense.org/>.

"""
Defines an interface that user interface plug-ins must implement.
"""

import abc

class UserInterfaceInterface(metaclass=abc.ABCMeta):
	"""
	Interface that user interface plug-ins must implement.

	It defines functions to start and stop the interface, and to wait until the
	user interface is finished.
	"""

	@abc.abstractmethod
	def join(self):
		"""
		.. function:: join()
		Blocks the calling thread until the user interface has stopped.
		"""

	@abc.abstractmethod
	def start(self):
		"""
		.. function:: start()
		Starts the user interface.

		Starting a user interface that has already started should have no
		effect, even if the user interface was stopped since. User interfaces
		are one-shot instances.
		"""

	@abc.abstractmethod
	def stop(self):
		"""
		.. function:: stop()
		Stops the user interface.

		This may still give the user interface time to close down. It should
		behave like the SIGTERM Unix signal. The method may only return after
		the interface has stopped.
		"""