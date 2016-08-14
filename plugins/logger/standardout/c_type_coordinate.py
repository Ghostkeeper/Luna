#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a data structure for the Windows API to put its coordinate data in.

This allows communication with the Windows API.
"""

import ctypes #To communicate to the Windows API.

class CTypeCoordinate(ctypes.Structure):
	"""
	C-type data structure representing a coordinate pair.

	This data structure must exactly match the COORD structure as described in
	the `MSDN documentation`_.

	.. _MSDN documentation: https://msdn.microsoft.com/en-us/library/windows/desktop/ms682119.aspx
	"""
	_fields_ = [
		("X", ctypes.c_short), #Horizontal coordinate.
		("Y", ctypes.c_short) #Vertical coordinate.
	]
	"""
	The fields in this structure.
	"""