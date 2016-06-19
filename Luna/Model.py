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
Provides a system for the model part of the model-view-presenter paradigm.

To use the model system properly, the following code changes are required:
- Give all classes that are part of the model the ``@model`` decorator.
- To let the view update whenever the model is changed, call the ``listen``
  function of the model. Supply a callable object that must be called whenever a
  change is made to the model.
- The listener must be callable without any parameters.
"""

import functools #To retain the documentation and name of the wrapped functions by these decorators.
import inspect #To check if listeners are bound methods, so we need to make a different type of reference then.
import weakref #To automatically remove listeners if their class instances are removed.

def model(originalClass):
	"""
	.. function:: model(originalClass)
	Decorator that modifies a class such that it becomes part of the model.

	This adds a ``listen`` function to the class, which can be used to listen to
	any or all changes to the class. This intended to be used by a viewer to
	update its view of the model towards the user.

	:param originalClass: The class to turn into a part of the model.
	:return: The same class, transformed to allow listening to its members.
	"""
	#Replace the initialisation to add initialisation of the dictionaries of listeners.
	originalInit = originalClass.__init__
	@functools.wraps(originalClass.__init__)
	def newInit(self,*args,**kwargs):
		self.__listening = False
		self.__attributeListeners = {} #For each attribute, contains a set of listeners. To be lazily filled when listeners hook in.
		self.__instanceListeners = set() #Set of listeners that listen to ALL changes in the instance.
		self.__listening = True
		originalInit(self,*args,**kwargs)
	originalClass.__init__ = newInit

	#Replace all methods that could change the instance.
	changingFunctions = ["__delattr__","__delitem__","__iadd__","__iand__","__ifloordiv__","__ilshift__","__imatmul__","__imod__","__imul__","__ior__","__ipow__","__irshift__","__isub__","__itruediv__","__ixor__","__setitem__","append"] #Not __setattr__! It'll be replaced with a special function.
	for functionName in [functionName for functionName in changingFunctions if hasattr(originalClass,functionName)]:
		oldFunction = getattr(originalClass,functionName)
		@functools.wraps(oldFunction)
		def newFunction(self,*args,**kwargs):
			result = oldFunction(self,*args,**kwargs)
			if not self.__listening:
				return result
			for listener in self.__instanceListeners:
				try:
					listener()()
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self.__instanceListeners.remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
			return result
		setattr(originalClass,functionName,newFunction) #Replace the function with a hooked function.

	#Replace __setattr__ with a special one that alerts the attribute listeners.
	oldSetattr = originalClass.__setattr__
	@functools.wraps(oldSetattr)
	def newSetattr(self,name,value):
		oldSetattr(self,name,value)
		if not self.__listening:
			return
		for listener in self.__instanceListeners: #Instance listeners always need to be called.
			try:
				listener()()
			except TypeError:
				if not listener: #Garbage collection nicked it!
					self.__instanceListeners.remove(listener)
				else: #An actual TypeError raised by the listener. Need to pass this on.
					raise
		if name in self.__attributeListeners:
			for listener in self.__attributeListeners[name]:
				try:
					listener()()
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self.__attributeListeners[name].remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
	originalClass.__setattr__ = newSetattr

	def listen(self,listener,attribute = None):
		"""
		.. function:: listen(listener[,attribute])
		Causes a listener to be called when the instance or an attribute of it
		changes.

		If no attribute is provided, the callable will be called when anything
		changes in the instance. If an attribute is provided, the callable will
		only be called when the specified attribute is changed.

		Note that the listening is 'shallow'. That means that if some
		attribute's attribute is changed, no listeners will be called. Only
		changes to the contents of this instance itself will trigger a callback.

		:param listener: A callable object to call when any or all of the
		attributes in this instance changes.
		:param attribute: If provided, the listener will only be called when
		this attribute is changed. Must be a str if provided.
		"""
		#Take a weak reference to the listener.
		if inspect.ismethod(listener) and hasattr(listener,"__self__"): #Is a bound method.
			listener = weakref.WeakMethod(listener) #Then we use the special WeakMethod that destroys the reference if the instance this method is bound to is destroyed.
		else:
			listener = weakref.ref(listener)

		if type(attribute) is str: #We are listening to a specific attribute.
			if not attribute in self.__attributeListeners:
				self.__attributeListeners[attribute] = set()
			self.__attributeListeners[attribute].add(listener)
		else: #We are listening to all changes.
			self.__instanceListeners.add(listener)
	originalClass.listen = listen

	return originalClass