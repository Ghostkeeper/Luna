#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a system for the model part of the model-view-presenter paradigm.

To use the model system properly, the following code changes are required:

- Give all classes that are part of the model the ``@model`` decorator.
- To let the view update whenever the model is changed, call the ``listen``
  function of the model. Supply a callable object that must be called whenever a
  change is made to the model.
- The listener must be callable without any parameters.
"""

import functools #To copy documentation to function wrappers and for partial function calls.
import inspect #To check if listeners are bound methods, so we need to make a different type of reference then.
import weakref #To automatically remove listeners if their class instances are removed.

def model(original_class):
	"""
	Decorator that modifies a class such that it becomes part of the model.

	This adds a ``listen`` function to the class, which can be used to listen to
	any or all changes to the class. This intended to be used by a viewer to
	update its view of the model towards the user.

	:param original_class: The class to turn into a part of the model.
	:return: The same class, transformed to allow listening to its members.
	"""
	#Replace the initialisation to add initialisation of the dictionaries of listeners.
	original_init = original_class.__init__

	@functools.wraps(original_class.__init__)
	def new_init(self, *args, **kwargs):
		"""
		Initialises the model such that lists of listeners are tracked.

		:param self: The model instance.
		:param args: Positional arguments passed to the model's ``__init__``.
		:param kwargs: Key-word arguments passed to the model's ``__init__``.
		"""
		#This function is only called when self is the original_class and only references fields defined in this module, so we can safely allow protected access.
		#pylint: disable=protected-access
		self._listening = False
		self._attribute_listeners = {} #For each attribute, contains a set of listeners. To be lazily filled when listeners hook in.
		self._instance_listeners = set() #Set of listeners that listen to ALL changes in the instance.
		self._listening = True
		original_init(self, *args, **kwargs)
	original_class.__init__ = new_init

	#Replace all methods that could change the instance.
	changing_functions = ["__delattr__", "__delitem__", "__iadd__", "__iand__", "__ifloordiv__", "__ilshift__", "__imatmul__", "__imod__", "__imul__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__itruediv__", "__ixor__", "__setitem__", "append"] #Not __setattr__! It'll be replaced with a special function.
	for function_name in [function_name for function_name in changing_functions if hasattr(original_class, function_name)]:
		old_function = getattr(original_class, function_name)

		@functools.wraps(old_function)
		def new_function(old_function, self, *args, **kwargs):
			"""
			Changes the model and calls the instance listeners of the model.

			:param old_function: The function that changes the model.
			:param self: The model instance.
			:param args: Positional arguments passed to the function that
				changes the model.
			:param kwargs: Key-word arguments passed to the function that
				changes the model.
			:return: The result of the function that changed the model.
			"""
			result = old_function(self, *args, **kwargs)
			#This function is only called when self is the original_class and only references fields defined in this module, so we can safely allow protected access.
			#pylint: disable=protected-access
			if not self._listening:
				return result
			for listener in self._instance_listeners:
				try:
					listener()()
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self._instance_listeners.remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
			return result
		setattr(original_class, function_name, functools.partial(new_function, old_function)) #Replace the function with a hooked function.

	#Replace __setattr__ with a special one that alerts the attribute listeners.
	old_setattr = original_class.__setattr__

	@functools.wraps(old_setattr)
	def new_setattr(self, name, value):
		"""
		Changes an attribute of the model and calls the listeners of the model.

		It calls the attribute listeners of the changed attribute, and all
		instance listeners.

		:param self: The model instance.
		:param name: The name of the attribute to change.
		:param value: The new value of the attribute.
		"""
		old_setattr(self, name, value)
		#This function is only called when self is the original_class and only references fields defined in this module, so we can safely allow protected access.
		#pylint: disable=protected-access
		if not self._listening:
			return
		for listener in self._instance_listeners: #Instance listeners always need to be called.
			try:
				listener()()
			except TypeError:
				if not listener: #Garbage collection nicked it!
					self._instance_listeners.remove(listener)
				else: #An actual TypeError raised by the listener. Need to pass this on.
					raise
		if name in self._attribute_listeners:
			for listener in self._attribute_listeners[name]:
				try:
					listener()()
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self._attribute_listeners[name].remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
	original_class.__setattr__ = new_setattr

	def listen(self, listener, attribute=None):
		"""
		Causes a listener to be called when the instance or an attribute of it
		changes.

		If no attribute is provided, the callable will be called when anything
		changes in the instance. If an attribute is provided, the callable will
		only be called when the specified attribute is changed.

		Note that the listening is 'shallow'. That means that if some
		attribute's attribute is changed, no listeners will be called. Only
		changes to the contents of this instance itself will trigger a callback.

		:param self: The instance to listen to for changes.
		:param listener: A callable object to call when any or all of the
			attributes in this instance changes.
		:param attribute: If provided, the listener will only be called when
			this attribute is changed. Must be a str if provided.
		"""
		#Take a weak reference to the listener.
		if inspect.ismethod(listener) and hasattr(listener, "__self__"): #Is a bound method.
			listener = weakref.WeakMethod(listener) #Then we use the special WeakMethod that destroys the reference if the instance this method is bound to is destroyed.
		else:
			listener = weakref.ref(listener)

		#This function is only called when self is the original_class and only references fields defined in this module, so we can safely allow protected access.
		#pylint: disable=protected-access
		if type(attribute) is str: #We are listening to a specific attribute.
			if attribute not in self._attribute_listeners:
				self._attribute_listeners[attribute] = set()
			self._attribute_listeners[attribute].add(listener)
		else: #We are listening to all changes.
			self._instance_listeners.add(listener)
	original_class.listen = listen

	return original_class