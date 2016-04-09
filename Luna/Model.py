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

To use the model system properly, the following code changes are required:
- Give all classes that are part of the model the ``@model`` decorator.
- To let the view update whenever the model is changed, call the ``listenTo``
  function of the model. Supply the member of the model that contains the data,
  and a reference to the function in the view that will update the view.
- The listening functions of the view must have no parameters other than
  ``self``. Otherwise they can't be called by the signalling system.
"""

from functools import wraps #To retain the documentation and name of the wrapped functions by these decorators.
from inspect import getargspec #Getting the number of arguments of a function, and setting up listeners for every member.
from weakref import WeakKeyDictionary #To automatically remove listeners and signallers if their class instances are removed.

from Luna.Logger import warning

class __StaticFunctionObject:
	"""
	Placeholder class to register static functions with.

	It must be possible to make a weak reference to the object that static
	functions are registered with. Therefore we create this class to be able to
	make a placeholder instance that is weakly referenced.
	"""

__static = __StaticFunctionObject()
"""
Instance to be used as key for static functions to keep them listed in the
WeakKeyDictionary of the listeners.

If a function has no __self__, it will get listed under this instance in the
listener dictionaries. Since this instance is never garbage collected, the entry
is never removed from the list of listeners.
"""
def combineMetaTypes(meta,*bases):
	"""
	.. function:: combineMetaTypes(meta[,bases]*)
	Combines an original class with a meta class.

	This overwrites the special properties of the original class with those of
	the meta class.
	:param meta: The meta class to combine with.
	:param bases: The base classes of the type.
	:return: A new type combining the original class with the specified meta
	class.
	"""
	return meta("CombinedBaseClass",bases,{})

class _SubModelMetaProperties(object):
	"""
	A meta class for the SubModel class.

	Some properties of an object cannot be emulated with simple wrapping. Even
	if you'd define them in the SubModel wrapper, the properties of the SubModel
	itself will take precedence over the manually defined properties. This meta
	class will still define them by copying the properties into the SubModel at
	creation.
	"""

	@property
	def __module__(self):
		"""
		.. function:: __module__
		Gets the name of the module the wrapped object was defined in.

		:return: The name of the module the wrapped object was defined in.
		"""
		return self.__wrapped__.__module__

	@__module__.setter
	def __module__(self,value):
		"""
		.. function:: __module__ = value
		Changes the name of the module the wrapped object is defined in.

		This constitutes a change of the model, and therefore triggers a signal.

		:param value: The new name of the module the wrapped object is defined
		in.
		"""
		self.__wrapped__.__module__ = value
		self.signal()

	@property
	def __doc__(self):
		"""
		.. function:: __doc__
		Gets the documentation string of the wrapped object, or None if
		unavailable.

		This is not inherited by subclasses.
		:return: The documentation of the wrapped object.
		"""
		return self.__wrapped__.__doc__

	@__doc__.setter
	def __doc__(self,value):
		"""
		.. function:: __doc__ = value
		Changes the documentation string of the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.

		:param value: The new documentation.
		"""
		self.__wrapped__.__doc__ = value
		self.signal()

	@property
	def __dict__(self):
		"""
		.. function:: __dict__
		Gets the namespace of the wrapped object, supporting arbitrary
		attributes.

		This overwrites __dict__ of the wrapper, so that ``vars()`` works as if
		it were called on the wrapped object too.
		:return: The namespace of the wrapped object.
		"""
		return self.__wrapped__.__dict__

	@property
	def __weakref__(self):
		"""
		.. function:: __weakref__
		Gets a weak reference to the wrapped object.

		Weak references do not count as references for the garbage collector,
		meaning that having a weak reference will not prevent the wrapped object
		from being garbage collected, but still allows access. The reference
		will become ``None`` if the object is garbage collected.

		While the wrapper is transparent for accessing normal references via
		each of the functions the wrapper defines, it is not transparent to
		accessing via weak references. This will overwrite the weak reference of
		the wrapper with the weak reference of the wrapped object so that
		accessing the object by its weak reference will work.

		:return: A weak reference to the wrapped object.
		"""
		return self.__wrapped__.__weakref__

class __SubModelType(type):
	"""
	A type for the SubModel class, which replaces some special properties of the
	SubModel.

	This makes even those special properties take precedence over the properties
	of the SubModel class itself.
	"""

	def __new__(cls,name,bases,properties):
		"""
		.. function:: __new__([name[,bases[,properties]]])
		Adds the properties of the ``SubModelMetaProperties`` to the dictionary
		of the SubModel class.

		:param name: The typename of the sub model.
		:param bases: The base classes of the type.
		:param properties: A dictionary of the properties assigned to the type.
		:return: An instance of ``__SubModelType``.
		"""
		properties.update(vars(_SubModelMetaProperties)) #Overwrite the old properties.
		return type.__new__(cls,name,bases,properties)

class __SubModel(combineMetaTypes(__SubModelType)):
	"""
	A class that wraps around an object, notifying a parent when the wrapped
	object is modified.

	The sub-model has a parent class which gets notified when any function is
	called that modifies the wrapped object.
	"""

	__slots__ = "__wrapped__"
	"""
	Defines the memory slots for the class.

	This can be used to optimise the memory usage of the class, by preventing
	unnecessary memory allocation.

	In this case it is used to make sure that the __wrapped__ slot is present
	even when the __slots__ is defined by the wrapped object. The __slots__ of
	the wrapped object will not be present in the SubModel instance.
	"""

	def __init__(self,wrapped,parent):
		"""
		.. function:: SubModel(wrapped,parent)
		Creates a new SubModel instance that pretends to be the wrapped object.

		:param wrapped: The object around which to wrap.
		:param parent: The parent object to notify whenever the wrapped object
		gets changed.
		"""
		object.__setattr__(self,"__wrapped__",wrapped) #Use __setattr__ of the superclass since that is not overwritten.
		object.__setattr__(self,"__parent",parent)

		#You can't set __qualname__ to be a function (with a @property decorator like below). Therefore we must copy it here.
		try:
			object.__setattr__(self,"__qualname__",wrapped.__qualname__)
		except AttributeError: #No qualified name.
			pass

	def __abs__(self):
		"""
		.. function:: __abs__()
		Gives the absolute value of the wrapped object.

		:return: The absolute value of the wrapped object.
		"""
		return self.__wrapped__.__abs__()

	def __add__(self,other):
		"""
		.. function:: __add__(other)
		Add the specified object to the wrapped object.

		:param other: The object to add to the wrapped object.
		:return: The sum of the two objects.
		"""
		return self.__wrapped__.__add__(other)

	def __and__(self,other):
		"""
		.. function:: __and__(other)
		Computes the logical and of the wrapped object and the specified object.

		The result is ``True`` only if both the wrapped object and the specified
		object are ``True``.

		:param other: The object to take the and with.
		:return: The logical and of the wrapped object and the specified object.
		"""
		return self.__wrapped__.__and__(other)

	@property
	def __annotations__(self):
		"""
		.. function:: __annotations__
		Gets a dictionary containing annotations of parameters of the wrapped
		object.

		The keys of the dictionary are the parameter names, and ``return`` for
		the return annotation, if provided. This only applies to callable
		objects.

		:return: A dictionary containing annotations of parameters of the
		wrapped object.
		"""
		return self.__wrapped__.__annotations__

	@__annotations__.setter
	def __annotations__(self,value):
		"""
		.. function:: __annotations__ = value
		Sets the annotations of parameters of the wrapped object.

		This only applies to callable objects.

		This constitutes a change of the model, and therefore triggers a signal.

		:param value: The new annotations of parameters. This must be a
		dictionary, whose keys are parameter names. The ``return`` key is for
		the return annotation, if provided.
		"""
		self.__wrapped__.__annotations__ = value
		self.signal()

	def __bool__(self):
		"""
		.. function:: __bool__()
		Tests the truth of the wrapped object.

		Called to implement truth value testing and the built-in operation
		``bool()``; should return ``False`` or ``True``. When this method is not
		defined, ``__len__()`` is called, if it is defined, and the object is
		considered true if its result is nonzero. If a class defines neither
		``__len__()`` nor ``__bool__()``, all its instances are considered true.
		:return: ``True`` or ``False``, depending on the truth value of the
		wrapped object.
		"""
		return self.__wrapped__.__bool__()

	def __bytes__(self):
		"""
		.. function:: __bytes__
		Computes a byte-string representation of the wrapped object.

		:return: A byte-string representation of the wrapped object.
		"""
		return self.__wrapped__.__bytes__()

	def __call__(self,*args,**kwargs):
		"""
		.. function:: __call__(...)
		Calls the wrapped object.

		This executes the wrapped object if it is a callable type, such as a
		function.

		:param args: Any positional arguments to call the wrapped object with.
		:param kwargs: Any keyword arguments to call the wrapped object with.
		:return: The return value the wrapped object gave.
		"""
		return self.__wrapped__.__call__(*args,**kwargs)

	@property
	def __class__(self):
		"""
		.. function:: __class__
		Gets the class of the wrapped object.

		:return: The class of the wrapped object.
		"""
		return self.__wrapped__.__class__

	@__class__.setter
	def __class__(self,value):
		"""
		.. function:: __class__ = value
		Changes the class of the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.
		:param value: The new class of the wrapped object.
		"""
		self.__wrapped__.__class__ = value
		self.signal()

	def __contains__(self,item):
		"""
		.. function:: __contains__(item)
		Checks whether the wrapped object contains the specified item.

		:param item: The item to check whether it is in the wrapped object.
		:return: ``True`` if the specified item is in the wrapped object, or
		``False`` otherwise.
		"""
		return self.__wrapped__.__contains__(item)

	def __delattr__(self,name):
		"""
		.. function:: __delattr__(name)
		Deletes an attribute from the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.

		:param name: The name of the attribute to delete.
		"""
		if name.startswith("_self_"): #It is an instance attribute.
			object.__delattr__(self,name)
		elif name == "__wrapped__": #Can't allow this.
			raise TypeError("__wrapped__ is a reserved name by the __SubModel wrapper.")
		elif name == "__qualname__": #Trying to delete the qualified name, so we must update it here too.
			object.__delattr__(self,name)
			delattr(self.__wrapped__,name)
		elif hasattr(type(self),name): #It is a class attribute.
			object.__delattr__(self,name)
		else: #Normal case.
			delattr(self.__wrapped__,name)
		self.signal()

	def __delitem__(self,key):
		"""
		.. function:: __delitem__(key)
		Deletes an item with the specified key from the wrapped object.

		If ``key`` is of an inappropriate type, a ``TypeError`` may be raised;
		if of a value outside the set of indices for the sequence (after any
		special interpretation of negative values), ``IndexError`` should be
		raised. For mapping types, if ``key`` is missing (not in the container),
		``KeyError`` should be raised.

		This constitutes a change in the model, and therefore triggers a signal.

		:param key: The key of the item to delete.
		"""
		self.__wrapped__.__delitem__(key)
		self.signal()

	def __dir__(self):
		"""
		.. function:: __dir__()
		Gets a sequence of all attributes of the wrapped object.

		Called when ``dir()`` is called on the object. A sequence must be
		returned. ``dir()`` converts the returned sequence to a list and sorts
		it.

		:return: A sequence of all attributes of the wrapped object.
		"""
		return self.__wrapped__.__dir__()

	def __divmod__(self,other):
		"""
		.. function:: __divmod__(other)
		Computes the quotient and remainder of a division of the wrapped object
		by the specified object.

		:param other: The object to divide the wrapped object by.
		:return: A tuple contining first the quotient, then the remainder of the
		division.
		"""
		return self.__wrapped__.__divmod__(other)

	def __enter__(self):
		"""
		.. function:: __enter__()
		Enter the runtime context related to the wrapped object.

		The ``with`` statement will bind this method's return value to the
		target(s) specified in the ``as`` clause of the statement, if any.

		:return: The wrapped object's context.
		"""
		return self.__wrapped__.__enter__()

	def __eq__(self,other):
		"""
		.. function:: __eq__(other)
		Computes whether the wrapped object is equal to the other.

		:param other: The object to compare the wrapped object with.
		:return: ``True`` if the wrapped object is equal to the specified
		object, or ``False`` otherwise.
		"""
		return self.__wrapped__.__eq__(other)

	def __exit__(self,exceptionType,exceptionValue,traceback):
		"""
		.. function:: __exit__(exceptionType,exceptionValue,traceback)
		Exit the runtime context related to the wrapped object.

		The parameters describe the exception that caused the context to be
		exited. If the context was exited without an exception, all three
		arguments must be ``None``. If an exception is supplied, and the method
		wishes to suppress the exception (i.e. prevent it from being
		propagated), it should return a ``True`` value. Otherwise, the exception
		will be processed normally upon exit from this method.

		:param exceptionType: The type of the exception that caused the context
		to be exited, or ``None`` if there was no exception.
		:param exceptionValue: The exception that caused the context to be
		exited, or ``None`` if there was no exception.
		:param traceback: A traceback that led to the exception that caused the
		context to be exited, or ``None`` if there was no exception.
		:return: ``True`` if the exception should be suppressed by the calling
		function, or ``False`` if it needn't be.
		"""
		return self.__wrapped__.__exit__(exceptionType,exceptionValue,traceback)

	def __float__(self):
		"""
		.. function:: __float__()
		Returns a floating point representation of the wrapped object.

		:return: A floating point representation of the wrapped object.
		"""
		return self.__wrapped__.__float__()

	def __floordiv__(self,other):
		"""
		.. function:: __floordiv__(other)
		Divides the wrapped object by the specified object, rounding down to the
		nearest whole.

		:param other: The object to divide the wrapped object by.
		:return: The division of the wrapped object by the specified object,
		rounded down to the nearest whole.
		"""
		return self.__wrapped__.__floordiv__(other)

	def __ge__(self,other):
		"""
		.. function:: __ge__(other)
		Computes whether the wrapped object is greater than or equal to the
		other.

		:param other: The object to compare the wrapped object with.
		:return: ``False`` if the wrapped object is less than the specified
		object, or ``True`` otherwise.
		"""
		return self.__wrapped__.__ge__(other)

	def __getattr__(self,name):
		"""
		.. function:: __getattr__(name)
		Gets the value of an attribute.

		Called when an attribute lookup has not found the attribute in the usual
		places (i.e. it is not an instance attribute nor is it found in the
		class tree for ``self``). This method should return the (computed)
		attribute value or raise an ``AttributeError`` exception.

		Note that if the attribute is found through the normal mechanism,
		``__getattr__()`` is not called. (This is an intentional asymmetry
		between ``__getattr__()`` and ``__setattr__()``.) This is done both for
		efficiency reasons and because otherwise ``__getattr__()`` would have no
		way to access other attributes of the instance. Note that at least for
		instance variables, you can fake total control by not inserting any
		values in the instance attribute dictionary (but instead inserting them
		in another object). See the ``__getattribute__()`` method below for a
		way to actually get total control over attribute access.

		:param name: The attribute name.
		:return: The value of the specified attribute.
		"""
		if name == "__wrapped__": #The __init__() method is not called yet, since the qualified name is incorrect.
			raise ValueError("Cannot change the wrapped object before the wrapper is initialised.")
		return self.__wrapped__.__getattribute__(name)

	def __getitem__(self,key):
		"""
		.. function:: __getitem__(key)
		Gets the specified element from the wrapped object.

		If ``key`` is of an inappropriate type, a ``TypeError`` may be raised;
		if of a value outside the set of indices for the sequence (after any
		special interpretation of negative values), ``IndexError`` should be
		raised. For mapping types, if ``key`` is missing (not in the container),
		``KeyError`` should be raised.

		:param key: The key of the item to get.
		:return: The value of the item to get.
		"""
		return self.__wrapped__.__getitem__(key)

	def __gt__(self,other):
		"""
		.. function:: __gt__(other)
		Computes whether the wrapped object is greater than the other.

		:param other: The object to compare the wrapped object with.
		:return: ``True`` if the wrapped object is greater than the specified
		object, or ``False`` otherwise.
		"""
		return self.__wrapped__.__gt__(other)

	def __hash__(self):
		"""
		.. function:: __hash__()
		Computes an integer differentiating the wrapped object from other
		instances.

		Called by built-in function ``hash()`` and for operations on members of
		hashed collections including ``set``, ``frozenset`` and ``dict``.
		``__hash__()`` should return an integer. The only required property is
		that objects which compare equal have the same hash value; it is advised
		to somehow mix together (e.g. using exclusive or) the hash values for
		the components of the object that also play a part in comparison of
		objects.
		:return: An integer differentiating the wrapped object from other
		instances.
		"""
		return self.__wrapped__.__hash__()

	def __hex__(self):
		"""
		.. function:: __hex__()
		Converts the wrapped object to a hexadecimal string.

		:return: A hexadecimal representation of the wrapped object.
		"""
		return self.__wrapped__.__hex__()

	def __iadd__(self,other):
		"""
		.. function:: __iadd__(other)
		Add the specified object to the wrapped object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to add to the wrapped object.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__iadd__(other)
		self.signal()
		return self

	def __iand__(self,other):
		"""
		.. function:: __iand__(other)
		Computes the logical and of the wrapped object and the specified object
		in-place.

		The wrapped object becomes ``True`` only if both the original wrapped
		object and the specified object are ``True``.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to take the and with.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__iand__(other)
		self.signal()
		return self

	def __ifloordiv__(self,other):
		"""
		.. function:: __ifloordiv__(other)
		Divides the wrapped object by the specified object in-place, rounding
		down to the nearest whole.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to divide the wrapped object by.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__ifloordiv__(other)
		self.signal()
		return self

	def __ilshift__(self,other):
		"""
		.. function:: __ilshift__(other)
		Computes the wrapped object shifted to the left by the specified object
		in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The amount to shift left by.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__ilshift__(other)
		self.signal()
		return self

	def __imatmul__(self,other):
		"""
		.. function:: __imatmul__(other)
		Computes the matrix multiplication of the wrapped object and the
		specified object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to matrix multiply the wrapped object with.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__imatmul__(other)
		self.signal()
		return self

	def __imod__(self,other):
		"""
		.. function:: __imod__(other)
		Computes the modulo of the wrapped object by the specified object
		in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The period of the modulo.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__imod__(other)
		self.signal()
		return self

	def __imul__(self,other):
		"""
		.. function:: __imul__(other)
		Multiply the wrapped object with the specified object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to multiply the wrapped object with.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__imul__(other)
		self.signal()
		return self

	def __index__(self):
		"""
		.. function:: __index__()
		Converts the wrapped object to an integer.

		The integer doesn't need to be a faithful representation of the wrapped
		object.

		:return: An integer representing the wrapped object.
		"""
		return self.__wrapped__.__index__()

	def __int__(self):
		"""
		.. function:: __int__()
		Returns an integer representation of the wrapped object.

		:return: An integer representation of the wrapped object.
		"""
		return self.__wrapped__.__int__()

	def __invert__(self):
		"""
		.. function:: __invert__()
		Returns the inversion of the wrapped object.

		:return: The inversion of the wrapped object.
		"""
		return self.__wrapped__.__invert__()

	def __ior__(self,other):
		"""
		.. function:: __ior__(other)
		Computes the logical or of the wrapped object and the specified object
		in-place.

		The wrapped object becomes ``True`` if the original wrapped object is
		``True``, the specified object is ``True``, or both.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to take the logical or with.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__ior__(other)
		self.signal()
		return self

	def __ipow__(self,other):
		"""
		.. function:: __ipow__(other[,modulo])
		Raise the wrapped object to the power of the specified object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The exponent of the power.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__ipow__(other)
		self.signal()
		return self

	def __irshift__(self,other):
		"""
		.. function:: __irshift__(other)
		Computes the wrapped object shifted to the right by the specified
		object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The amount to shift right by.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__irshift__(other)
		self.signal()
		return self

	def __isub__(self,other):
		"""
		.. function:: __isub__(other)
		Subtracts the specified object from the wrapped object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to subtract from the wrapped object.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__isub__(other)
		self.signal()
		return self

	def __iter__(self):
		"""
		.. function:: __iter__()
		Gets an iterator object that iterates over the elements in the wrapped
		object.

		For mappings, it should iterate over the keys of the wrapped object.

		:return: An iterator object that iterates over the elements in the
		wrapped object.
		"""
		return self.__wrapped__.__iter__()

	def __itruediv__(self,other):
		"""
		.. function:: __itruediv__(other)
		Divides the wrapped object by the specified object in-place.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to divide the wrapped object by.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__itruediv__(other)
		self.signal()
		return self

	def __ixor__(self,other):
		"""
		.. function:: __ixor__(other)
		Computes the exclusive or of the wrapped object and the specified
		object in-place.

		The wrapped object becomes ``True`` if either the original wrapped
		object or the specified object is ``True``, but not both.

		This constitutes a change of the model, and therefore triggers a signal.

		:param other: The object to take the exclusive or with.
		:return: The wrapper, after making the change.
		"""
		self.__wrapped__.__ixor__(other)
		self.signal()
		return self

	def __le__(self,other):
		"""
		.. function:: __le__(other)
		Computes whether the wrapped object is less than or equal to the other.

		:param other: The object to compare the wrapped object with.
		:return: ``False`` if the wrapped object is greater than the specified
		object, or ``True`` otherwise.
		"""
		return self.__wrapped__.__le__(other)

	def __len__(self):
		"""
		.. function:: __len__()
		Returns the number of elements the wrapped object consists of.

		:return: The number of elements the wrapped object consists of.
		"""
		return self.__wrapped__.__len__()

	def __long__(self):
		"""
		.. function:: __long__()
		Returns a long representation of the wrapped object.

		:return: A long representation of the wrapped object.
		"""
		return self.__wrapped__.__long__()

	def __lshift__(self,other):
		"""
		.. function:: __lshift__(other)
		Computes the wrapped object shifted to the left by the specified object.

		:param other: The amount to shift left by.
		:return: The wrapped object shifted to the left.
		"""
		return self.__wrapped__.__lshift__(other)

	def __lt__(self,other):
		"""
		.. function:: __lt__(other)
		Computes whether the wrapped object is less than the other.

		:param other: The object to compare the wrapped object with.
		:return: ``True`` if the wrapped object is less than the specified
		object, or ``False`` otherwise.
		"""
		return self.__wrapped__.__lt__(other)

	def __matmul__(self,other):
		"""
		.. function:: __matmul__(other)
		Computes the matrix multiplication of the wrapped object and the
		specified object.

		:param other: The object to matrix multiply the wrapped object with.
		:return: The matrix multiplication of the wrapped object and the
		specified object.
		"""
		return self.__wrapped__.__matmul__(other)

	def __mod__(self,other):
		"""
		.. function:: __mod__(other)
		Computes the modulo of the wrapped object by the specified object.

		:param other: The period of the modulo.
		:return: The modulo of the wrapped object by the specified object.
		"""
		return self.__wrapped__.__mod__(other)

	def __mul__(self,other):
		"""
		.. function:: __mul__(other)
		Multiply the wrapped object with the specified object.

		:param other: The object to multiply the wrapped object with.
		:return: The product of the wrapped object and the specified object.
		"""
		return self.__wrapped__.__mul__(other)

	@property
	def __name__(self):
		"""
		.. function:: __name__
		Gets the name of the wrapped object.

		:return: The name of the wrapped object.
		"""
		return self.__wrapped__.__name__

	@__name__.setter
	def __name__(self,value):
		"""
		.. function:: __name__ = value
		Changes the name of the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.
		:param value: The new name of the wrapped object.
		"""
		self.__wrapped__.__name__ = value
		self.signal()

	def __ne__(self,other):
		"""
		.. function:: __ne__(other)
		Computes whether the wrapped object is different from the other.

		:param other: The object to compare the wrapped object with.
		:return: ``False`` if the wrapped object is equal to the specified
		object, or ``True`` otherwise.
		"""
		return self.__wrapped__.__ne__(other)

	def __neg__(self):
		"""
		.. function:: __neg__()
		Gives the negative of the wrapped object.

		:return: The negative of the wrapped object.
		"""
		return self.__wrapped__.__neg__()

	def __oct__(self):
		"""
		.. function:: __oct__()
		Converts the wrapped object to an octal string.

		:return: An octal representation of the wrapped object.
		"""
		return self.__wrapped__.__oct__()

	def __or__(self,other):
		"""
		.. function:: __or__(other)
		Computes the logical or of the wrapped object and the specified object.

		The result is ``True`` if the wrapped object is ``True``, the specified
		object is ``True``, or both.

		:param other: The object to take the logical or with.
		:return: The logical or of the wrapped object and the specified object.
		"""
		return self.__wrapped__.__or__(other)

	def __pos__(self):
		"""
		.. function:: __pos__()
		Gives the positive representation of the wrapped object.

		:return: The positive representation of the wrapped object.
		"""
		return self.__wrapped__.__pos__()

	def __pow__(self,other,modulo = None):
		"""
		.. function:: __pow__(other[,modulo])
		Raise the wrapped object to the power of the specified object.

		If a modulo is provided, the result is computed in the period of that
		modulo. This might be more efficient to compute than the actual power.

		:param other: The exponent of the power.
		:param modulo: The period to reduce the result to, or ``None`` if the
		result should not be reduced by any modulo.
		:return: The wrapped object raised to the power of the specified object.
		"""
		return self.__wrapped__.__pow__(other,modulo)

	def __radd__(self,other):
		"""
		.. function:: __radd__(other)
		Add the wrapped object to the specified object.

		:param other: The object to add the wrapped object to.
		:return: The sum of the two objects.
		"""
		return self.__wrapped__.__radd__(other)

	def __rand__(self,other):
		"""
		.. function:: __rand__(other)
		Computes the logical and of the specified object and the wrapped object.

		The result is ``True`` only if both the wrapped object and the specified
		object are ``True``.

		:param other: The object to take the and with.
		:return: The logical and of the specified object and the wrapped object.
		"""
		return self.__wrapped__.__rand__(other)

	def __rdivmod__(self,other):
		"""
		.. function:: __rdivmod__(other)
		Computes the quotient and remainder of a division of the specified
		object by the wrapped object.

		:param other: The object to divide by the wrapped object.
		:return: A tuple contining first the quotient, then the remainder of the
		division.
		"""
		return self.__wrapped__.__rdivmod__(other)

	def __repr__(self):
		"""
		.. function:: __repr__()
		Computes an "official" string representation of the wrapped object.

		Called by the ``repr()`` built-in function. This will give a string of
		the form ``<(wrapper class) at (wrapper id) wrapping (wrapped class) at
		(wrapped id)>``. If the wrapped object defines no ``__str__()``, then
		``__repr__()`` is also used when an "informal" string representation of
		instances of that class is required.

		:return: An "official" string representation of the wrapped object.
		"""
		return "<{wrapperClass} at {wrapperID} representing {wrappedClass} at {wrappedID}".format(wrapperClass = type(self).__name__,wrapperID = id(self),wrappedClass = type(self.__wrapped__).__name__,wrappedID = id(self.__wrapped__))

	def __reversed__(self):
		"""
		.. function:: __reversed__()
		Implements reverse iteration.

		Called (if present) by the ``reversed()`` built-in. It should return a
		new iterator object that iterates over all the objects in the container
		in reverse order.
		:return: An iterator object that iterates over all the objects in the
		container n reverse order.
		"""
		return self.__wrapped__.__reversed__()

	def __rfloordiv__(self,other):
		"""
		.. function:: __rfloordiv__(other)
		Divides the specified object by the wrapped object, rounding down to the
		nearest whole.

		:param other: The object to divide by the wrapped object.
		:return: The division of the specified object by the wrapped object,
		rounded down to the nearest whole.
		"""
		return self.__wrapped__.__rfloordiv__(other)

	def __rlshift__(self,other):
		"""
		.. function:: __rlshift__(other)
		Computes the specified object shifted to the left by the wrapped object.

		:param other: The object to shift to the left.
		:return: The specified object shifted to the left.
		"""
		return self.__wrapped__.__rlshift__(other)

	def __rmatmul__(self,other):
		"""
		.. function:: __rmatmul__(other)
		Computes the matrix multiplication of the specified object and the
		wrapped object.

		:param other: The object to matrix multiply with the wrapped object.
		:return: The matrix multiplication of the specified object and the
		wrapped object.
		"""
		return self.__wrapped__.__rmatmul__(other)

	def __rmod__(self,other):
		"""
		.. function:: __rmod__(other)
		Computes the modulo of the specified object by the wrapped object.

		:param other: The object to take the modulo of.
		:return: The modulo of the specified object by the wrapped object.
		"""
		return self.__wrapped__.__rmod__(other)

	def __rmul__(self,other):
		"""
		.. function:: __rmul__(other)
		Multiply the specified object with the wrapped object.

		:param other: The object to multiply with the wrapped object.
		:return: The product of the specified object and the wrapped object.
		"""
		return self.__wrapped__.__rmul__(other)

	def __ror__(self,other):
		"""
		.. function:: __ror__(other)
		Computes the logical or of the specified object and the wrapped object.

		The result is ``True`` if the specified object is ``True``, the wrapped
		object is ``True``, or both.

		:param other: The object to take the logical or with.
		:return: The logical or of the specified object and the wrapped object.
		"""
		return self.__wrapped__.__ror__(other)

	def __round__(self,n = None):
		"""
		.. function:: __round__([n])
		Rounds the wrapped object.

		Called to implement the built-in functions ``complex()``, ``int()``,
		``float()`` and ``round()``.

		:param n: A specific representation length to round to.
		:return: A rounded version of the wrapped object.
		"""
		return self.__wrapped__.__round__(n)

	def __rpow__(self,other,modulo = None):
		"""
		.. function:: __rpow__(other[,modulo])
		Raise the specified object to the power of the wrapped object.

		If a modulo is provided, the result is computed in the period of that
		modulo. This might be more efficient to compute than the actual power.

		:param other: The base of the power.
		:param modulo: The period to reduce the result to, or ``None`` if the
		result should not be reduced by any modulo.
		:return: The specified object raised to the power of the wrapped object.
		"""
		return self.__wrapped__.__rpow__(other,modulo)

	def __rrshift__(self,other):
		"""
		.. function:: __rrshift__(other)
		Computes the specified object shifted to the right by the wrapped
		object.

		:param other: The object to shift right.
		:return: The specified object shifted to the right.
		"""
		return self.__wrapped__.__rrshift__(other)

	def __rshift__(self,other):
		"""
		.. function:: __rshift__(other)
		Computes the wrapped object shifted to the right by the specified
		object.

		:param other: The amount to shift right by.
		:return: The wrapped object shifted to the right.
		"""
		return self.__wrapped__.__rshift__(other)

	def __rsub__(self,other):
		"""
		.. function:: __rsub__(other)
		Subtracts the wrapped object from the specified object.

		:param other: The object to subtract the wrapped object from.
		:return: The difference between the specified object and the wrapped
		object.
		"""
		return self.__wrapped__.__rsub__(other)

	def __rtruediv__(self,other):
		"""
		.. function:: __truediv__(other)
		Divides the specified object by the wrapped object.

		:param other: The object to divide by the wrapped object.
		:return: The division of the specified object by the wrapped object.
		"""
		self.__wrapped__.__rtruediv__(other)

	def __rxor__(self,other):
		"""
		.. function:: __rxor__(other)
		Computes the exclusive or of the specified object and the wrapped
		object.

		The result is ``True`` if either the specified object or the wrapped
		object is ``True``, but not both.

		:param other: The object to take the exclusive or with.
		:return: The exclusive or of the spedified object and the wrapped
		object.
		"""
		return self.__wrapped__.__rxor__(other)

	def __setattr__(self,name,value):
		"""
		.. function:: __setattr__(name,value)
		Assigns a value to an attribute.

		Called when an attribute assignment is attempted. This is called instead
		of the normal mechanism (i.e. store the value in the instance
		dictionary).

		If ``__setattr__()`` wants to assign to an instance attribute, it should
		call the base class method with the same name, for example,
		``object.__setattr__(self,name,value)``.

		This constitutes a change of the model, and therefore triggers a signal.

		:param name: The attribute name.
		:param value: The value to be assigned to the attribute.
		"""
		if type(value).__name__ == type(self).__name__: #If the value is already a wrapper, unwrap it first and wrap it in a new wrapper, so we can set the parent without disturbing the old parent.
			value = object.__getattribute__(value,"__wrapped__")
		value = type(self)(value,self) #Have to go via type(self) since the class of this object will get the class of the wrapped element.

		if name.startswith("_self_"): #Assignment via self to an instance attribute.
			object.__setattr__(self,name,value)
		elif name == "__wrapped__": #Trying to change the wrapped object (from the wrapper's init).
			object.__setattr__(self,name,value)
			try: #Update the qualified name.
				object.__delattr__(self,"__qualname__")
			except AttributeError: #No qualified name.
				pass
			try:
				object.__setattr__(self,"__qualname__",value.__qualname__)
			except AttributeError:
				pass
		elif name == "__qualname__": #Trying to change the qualified name.
			setattr(self.__wrapped__,name,value)
			object.__setattr__(self,name,value) #Also update the qualified name of the wrapper.
		elif hasattr(type(self),name): #Other attributes of the wrapper.
			object.__setattr__(self,name,value)
		else: #Class attributes.
			setattr(self.__wrapped__,name,value)
		self.signal()

	def __setitem__(self,key,value):
		"""
		.. function:: __setitem__(key,value)
		Changes the value of a specified item in the wrapped object, or adds it
		if the key is not yet in the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.

		:param key: The key of the item to set.
		:param value: The value of the item to set.
		"""
		if type(value).__name__ == type(self).__name__: #If the value is already a wrapper, unwrap it first and wrap it in a new wrapper, so we can set the parent without disturbing the old parent.
			value = object.__getattribute__(value,"__wrapped__")
		value = type(self)(value,self) #Have to go via type(self) since the class of this object will get the class of the wrapped element.

		self.__wrapped__.__setitem__(key,value)
		self.signal()

	def __str__(self):
		"""
		.. function:: __str__()
		Computes the "informal" or nicely printable string representation of the
		wrapped object.

		Called by ``str(object)`` and the built-in functions ``format()`` and
		``print()``.
		:return: A nicely printable string representation of the wrapped object.
		"""
		return self.__wrapped__.__str__()

	def __sub__(self,other):
		"""
		.. function:: __sub__(other)
		Subtracts the specified object from the wrapped object.

		:param other: The object to subtract from the wrapped object.
		:return: The difference between the wrapped object and the specified
		object.
		"""
		return self.__wrapped__.__sub__(other)

	def __truediv__(self,other):
		"""
		.. function:: __truediv__(other)
		Divides the wrapped object by the specified object.

		:param other: The object to divide the wrapped object by.
		:return: The division of the wrapped object by the specified object.
		"""
		self.__wrapped__.__truediv__(other)

	def __xor__(self,other):
		"""
		.. function:: __xor__(other)
		Computes the exclusive or of the wrapped object and the specified
		object.

		The result is ``True`` if either the wrapped object or the specified
		object is ``True``, but not both.

		:param other: The object to take the exclusive or with.
		:return: The exclusive or of the wrapped object and the specified
		object.
		"""
		return self.__wrapped__.__xor__(other)

	def append(self,item):
		"""
		.. function:: append(item)
		Adds the specified item at the end of the wrapped object.

		This constitutes a change of the model, and therefore triggers a signal.

		:param item: The item to add to the wrapped object.
		"""
		if type(item).__name__ == type(self).__name__: #If the value is already a wrapper, unwrap it first and wrap it in a new wrapper, so we can set the parent without disturbing the old parent.
			item = object.__getattribute__(item,"__wrapped__")
		item = type(self)(item,self) #Have to go via type(self) since the class of this object will get the class of the wrapped element.

		self.__wrapped__.append(item)
		self.signal()

	def signal(self):
		"""
		.. function:: signal()
		Signals this class that one of its children has been modified.
		"""
		if object.__getattribute__(self,"__parent"):
			object.__getattribute__(self,"__parent").signal()

def model(originalClass):
	"""
	.. function:: model(originalClass)
	Decorator that modifies a class such that it becomes part of the model.

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

		if "__self__" not in dir(function): #Function is static. There is no self.
			instance = __static
		else:
			instance = function.__self__

		if not instance in self.__listeners[member]:
			self.__listeners[member][instance] = []

		self.__listeners[member][instance].append(function) #Add this function as listener.
	originalClass.listenTo = listenTo #Add the listenTo method.

	return originalClass #Return a modified class.