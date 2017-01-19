#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a system for the model part of the model-view-presenter paradigm.

To use the model system properly, the following code changes are required:

- To let the view update whenever the model is changed, call the ``listen``
  function of the model. Supply a callable object that must be called whenever a
  change is made to the model.
- The listener must accept two parameters: the attribute that was changed and
  the new value for the attribute.
"""

import functools #To copy documentation to function wrappers and for partial function calls.
import inspect #To check if listeners are bound methods, so we need to make a different type of reference then.
import weakref #To automatically remove listeners if their class instances are removed.

def listen(listener, instance, attribute=None):
	"""
	Listen for changes of the specified attribute or the specified instance.

	If no attribute is provided, the listener will get called when any of the
	attributes of the specified field change. If an attribute is provided, the
	listener will only get called when the specified attribute is changed. The
	listener will get called with as first argument the attribute that changed
	(as a string) and as second argument the new value of the attribute.

	If the attribute was set, but set to the same value as it was before, the
	listeners are not called. It does not count as a change.

	Listening is "shallow". This means that internal changes inside the value of
	an attribute will not constitute a change. Only if the attribute itself has
	changed will it trigger the listeners.

	Listening to instances or attributes of instances requires changing the
	object inherently to add extra methods, overriding `__setattribute__`, and
	to add extra fields to hold the listeners. This is not possible if the class
	of the instance is defined natively (for instance with a `list` or `dict`)
	or if the class has a `__slots__` field. For those cases, it is advisable to
	use a transparent wrapper.
	:param listener: A callable object that takes two arguments for its call.
	The first argument should be interpreted as the name of the attribute that
	changed. The second argument should be interpreted as the new value for the
	attribute.
	:param instance: The instance to listen to for changes.
	:param attribute: If set, the name of the attribute of the instance to
	listen to for changes. If this is `None`, all attribute changes of the
	instance will cause the listener to be called.
	"""
	#Take a weak reference to the listener.
	if inspect.ismethod(listener) and hasattr(listener, "__self__"): #Is a bound method.
		listener = weakref.WeakMethod(listener) #Then we use the special WeakMethod that destroys the reference if the instance this method is bound to is destroyed.
	else:
		listener = weakref.ref(listener)

	if not hasattr(instance, "_instance_listeners") or not hasattr(instance, "_attribute_listeners"):
		_initialise_listeners(instance) #Create lists of listeners.

	#This function only accesses attributes that are defined by the _initialise_listeners, so we can safely allow protected member access.
	#pylint: disable=protected-access
	if type(attribute) is str: #We are listening to a specific attribute.
		if attribute not in instance._attribute_listeners:
			instance._attribute_listeners[attribute] = set()
		instance._attribute_listeners[attribute].add(listener)
	else: #We are listening to all changes.
		instance._instance_listeners.add(listener)

def _initialise_listeners(instance):
	"""
	Prepares an object for storing listeners to all or some of its attributes.
	:param instance: The instance to prepare for being listened to.
	"""
	#This function only defines new attributes. They should be protected because it should only be visible to this module. We can therefore safely allow protected member access.
	#pylint: disable=protected-access
	instance._attribute_listeners = {}
	instance._instance_listeners = set()

	#Make a copy of the instance's class to modify some methods of.
	modified_class = type(instance.__class__.__name__ + "_Model", instance.__class__.__bases__, dict(instance.__class__.__dict__))

	#Replace all methods that could change the instance.
	changing_methods = ["__delattr__", "__delitem__", "__iadd__", "__iand__", "__ifloordiv__", "__ilshift__", "__imatmul__", "__imod__", "__imul__", "__ior__", "__ipow__", "__irshift__", "__isub__", "__itruediv__", "__ixor__", "__setitem__", "append"] #Not __setattr__! It'll be replaced with a special function.
	for function_name in [function_name for function_name in changing_methods if hasattr(instance, function_name)]:
		old_method = getattr(instance, function_name)

		@functools.wraps(old_method)
		def new_function(old_method, self, *args, **kwargs):
			"""
			Changes the model and calls the instance listeners of the model.
			:param old_method: The method that changes the model.
			:param self: The model instance which is being listened to.
			:param args: Positional arguments passed to the method that changes
			the model.
			:param kwargs: Key-word arguments passed to the method that changes
			the model.
			:return: The result of the method that changed the model.
			"""
			result = old_method(self, *args, **kwargs)
			for listener in self._instance_listeners:
				try:
					listener()(function_name, None)
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self._instance_listeners.remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
			return result
		setattr(modified_class, function_name, functools.partial(new_function, old_method)) #Replace the method with a hooked method.

	#Replace __setattr__ with a special one that alerts the attribute listeners.
	old_setattr = instance.__setattr__

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
		old_value = getattr(self, name)
		old_setattr(name, value) #Note that self is not provided since old_setattr already gets __setattr__ from instance and is therefore a method-wrapper.
		if hasattr(self, name): #Only detect that we haven't actually changed the value if the value existed before setting.
			if old_value == getattr(self, name):
				return #Set to the same value it already had. No change!
		for listener in self._instance_listeners: #Instance listeners always need to be called.
			try:
				listener()(name, value)
			except TypeError:
				if not listener: #Garbage collection nicked it!
					self._instance_listeners.remove(listener)
				else: #An actual TypeError raised by the listener. Need to pass this on.
					raise
		if name in self._attribute_listeners:
			for listener in self._attribute_listeners[name]:
				try:
					listener()(name, value)
				except TypeError:
					if not listener: #Garbage collection nicked it!
						self._attribute_listeners[name].remove(listener)
					else: #An actual TypeError raised by the listener. Need to pass this on.
						raise
	modified_class.__setattr__ = new_setattr
	instance.__class__ = modified_class #Swap out the class of the object, and thereby change its methods.