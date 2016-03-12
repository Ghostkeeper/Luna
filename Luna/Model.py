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

from functools import wraps #To retain the documentation and name of the wrapped functions by these decorators.
from inspect import getargspec #Getting the number of arguments of a function, and setting up listeners for every member.
from weakref import WeakKeyDictionary,WeakSet #To automatically remove listeners and signallers if their class instances are removed.

from Luna.Logger import warning

def model(originalClass):
	"""
	.. function:: model(originalClass)
	Modifies a class such that it becomes part of the model.

	This adds signals for each of the class' members, and a ``listenTo`` method.
	Using the ``listenTo`` method, a different function can be registered to be
	called every time a certain member changes. This is intended to be used by a
	viewer to update its view of the model towards the user.

	:param originalClass: The class to turn into a part of the model.
	:return: The same class, but with added hooks into every of its members that
	can be listened to.
	"""
	originalInit = originalClass.__init__
	@wraps(originalClass.__init__)
	def newInit(self,*args,**kwargs): #Create a new __init__ function.
		self.__listeners = {}
		for member in dir(self): #Add a signal for all static members.
			#We're creating a WeakKeyDictionary that contains lists of methods.
			#These are keyed by the instance of the method, which is a weak reference.
			#So if the instance is removed, the methods are removed too.
			self.__listeners[member] = WeakKeyDictionary() #Keyed by instance, values are lists of functions.
		originalInit(self,*args,**kwargs)
	originalClass.__init__ = newInit #Replace the old __init__ with the new one.

	originalSetAttr = originalClass.__setattr__ #Create a new __setattr__ function.
	@wraps(originalSetAttr)
	def newSetAttr(self,name,value):
		originalSetAttr(self,name,value)
		if name == "__listeners": #Don't want this to be triggered before the listener construction has been set up.
			return
		if not name in self.__listeners: #Attribute added dynamically. Add a signal for it.
			self.__listeners[name] = WeakKeyDictionary()
		for instance in self.__listeners[name]: #Call anything that listens to this member.
			for listener in self.__listeners[name][instance]:
				listener()
	originalClass.__setattr__ = newSetAttr #Replace the old __setattr__ with the new one.

	def listenTo(self,member,function):
		"""
		.. function:: listenTo(member,function)
		Hooks a function to be called whenever the specified member is changed.

		Note that this only works on local members, not on static members.

		:param member: The name of the member to listen to, as string.
		:param function: The function to call whenever that member is changed.
		"""
		if not member in self.__listeners:
			warning("No member \"{member}\" found to listen to.",member = member)
			return

		if len(getargspec(function).args) > 1: #Function has arguments. Can't have that.
			warning("Listener function {function} must not have any arguments.",function = str(function))
			return

		if not function.__self__ in self.__listeners[member]:
			self.__listeners[member][function.__self__] = []

		self.__listeners[member][function.__self__].append(function) #Add this function as listener.
	originalClass.listenTo = listenTo #Add the listenTo method.

	return originalClass #Return a modified class.