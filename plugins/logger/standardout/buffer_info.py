#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

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