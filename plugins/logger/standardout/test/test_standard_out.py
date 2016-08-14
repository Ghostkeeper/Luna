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
Tests the behaviour of the standard_out logger implementation.
"""

import io #Provides a replacement I/O channel to mock stdout.
import sys #To capture stdout.
import luna.test_case #To get parametrised tests.

import standardout.standard_out #The module to test.

class TestStandardOut(luna.test_case.TestCase):
	"""
	Tests the behaviour of the standard_out logger implementation.
	"""

	def setUp(self):
		"""
		Prepares for a test by intercepting the stdout channel.
		"""
		self._actual_stdout = sys.stdout
		self._mock_stdout = io.StringIO()
		sys.stdout = self._mock_stdout #Swaps out stdout with something that we can verify the contents of.

	def tearDown(self):
		"""
		Restores the state of the stdout channel after tests.
		"""
		sys.stdout = self._actual_stdout
		self._mock_stdout.close()

	@luna.test_case.parametrise({
		"simple": {"message": "Message.", "title": "Title"},
		"empty": {"message": "", "title": ""},
		"multiline": {"message": "First line.\nSecond line.", "title": "Multiline"},
		"unicode": {"message": "☽", "title": "☾"}
	})
	def test_info(self, message, title):
		"""
		.. function:: test_info()
		Tests printing a simple info message.
		"""
		standardout.standard_out.info(message, title=title)
		self.assertIn(title, self._mock_stdout.getvalue())
		self.assertIn(message, self._mock_stdout.getvalue())

if __name__ == "__main__":
	unittest.main()