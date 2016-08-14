#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a data structure for the Windows API to put a rectangle in.

This allows communication with the Windows API.
"""

import ctypes #To communicate with the Windows API.

class CTypeRectangle(ctypes.Structure):
	"""
	C-type data structure to representing a rectangle.

	The rectangle consists of a position and a size.

	This data structure must exactly match the SMALL_RECT structure as described
	in the `MSDN documentation
	<https://msdn.microsoft.com/en-us/library/windows/desktop/ms686311.aspx>`.
	"""
	_fields_ = [
		("Left", ctypes.c_short), #Horizontal coordinate of left side.
		("Top", ctypes.c_short), #Vertical coordinate of top side.
		("Right", ctypes.c_short), #Horizontal coordinate of right side.
		("Bottom", ctypes.c_short) #Vertical coordinate of bottom side.
	]
	"""
	The fields in this structure.
	"""