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
Provides a data structure for the Windows API to put its buffer info data in.

This allows communication with the Windows API.
"""

import ctypes #To communicate with the Windows API.

from . import c_type_coordinate #To store the state of the console window on Windows.
from . import c_type_rectangle #To store the state of the console window on Windows.

class BufferInfo(ctypes.Structure):
	"""
	C-type data structure to store the state of the Windows stdout channel in.

	This data structure must exactly match the CONSOLE_SCREEN_BUFFER_INFO
	structure as described in the `MSDN documentation
	<https://msdn.microsoft.com/en-us/library/windows/desktop/ms682093.aspx>`.
	"""
	_fields_ = [
		("dwSize", c_type_coordinate.CTypeCoordinate), #Size of the window (in character rows and columns).
		("dwCursorPosition", c_type_coordinate.CTypeCoordinate), #Position of the caret.
		("wAttributes", ctypes.c_ushort), #The text attributes of the output channel, such as colour.
		("srWindow", c_type_rectangle.CTypeRectangle), #Position and size of the window relative to its parent display (in pixels).
		("dwMaximumWindowSize", c_type_coordinate.CTypeCoordinate) #Maximum window size given the current font size.
	]
	"""
	The fields in this structure.
	"""