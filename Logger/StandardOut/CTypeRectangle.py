#!/usr/bin/env python

#This is free and unencumbered software released into the public domain.
#
#Anyone is free to copy, modify, publish, use, compile, sell, or distribute this
#software, either in source code form or as a compiled binary, for any purpose,
#commercial or non-commercial, and by any means.
#
#In jurisdictions that recognize copyright laws, the author or authors of this
#software dedicate any and all copyright interest in the software to the public
#domain. We make this dedication for the benefit of the public at large and to
#the detriment of our heirs and successors. We intend this dedication to be an
#overt act of relinquishment in perpetuity of all present and future rights to
#this software under copyright law.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
#ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#For more information, please refer to <https://unlicense.org/>

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
		("Left",ctypes.c_short), #Horizontal coordinate of left side.
		("Top",ctypes.c_short), #Vertical coordinate of top side.
		("Right",ctypes.c_short), #Horizontal coordinate of right side.
		("Bottom",ctypes.c_short) #Vertical coordinate of bottom side.
	]
	"""
	The fields in this structure.
	"""