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

"""
Provides a system for the model part of the model-view-presenter paradigm.

For a safe model system, every model should follow the following rules:
- All data must be private inside a class (with field names starting with two
  underscores).
- All functions that change the data must have the ``setter`` decorator.
"""

from weakref import WeakKeyDictionary,WeakSet #To automatically remove listeners and signallers if their class instances are removed.

__listeners = WeakKeyDictionary()
"""
For each function, a set of functions that need to be called whenever the method
is called.

Entries of the dictionary will automatically get garbage collected once all
strong references to their class instances are removed. Entries of each listener
set will automatically get garbage collected once all strong references to their
class instances are removed.
"""

def signal(setter):
	"""
	.. function:: signal(setterFunction)
	Decorator indicating that a function can be registered with listeners.

	This decorator should be used for any method that changes the data in the
	model.
	:param setterFunction: The function to allow registering listeners with.
	:return: A new function that calls all listeners after calling the setter.
	"""
	global __listeners
	if not setter in __listeners: #Make an entry to track listeners of this function.
		__listeners[setter] = WeakSet()
	def newSetter(*args,**kwargs):
		setter(*args,**kwargs)
		for listener in __listeners[setter]: #Call all listeners.
			listener()
	return newSetter