#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Keeps track of all user interface plug-ins.

User interface plug-ins need to register here. Their implementations are stored
and may be called upon to start and communicate with the user.
"""

import collections #For namedtuple.

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid, and logging.

_UserInterface = collections.namedtuple("_UserInterface", "join start stop")
"""
Represents a user interface plug-in.

This named tuple has one field for every function in the user interface:
* join: Blocks the current thread until the user interface terminates.
* start: Starts the user interface.
* stop: Interrupts the user interface.
"""

_user_interfaces = {}
"""
The user interfaces that have been registered here so far, keyed by their
identities.
"""

def get_all_user_interfaces():
	"""
	Gets all user interfaces that have been registered here so far.

	:return: A dictionary of user interfaces, keyed by their identities.
	"""
	return _user_interfaces

def get_user_interface(identity):
	"""
	Gets a specific user interface plug-in object by identity.

	:param identity: The identity of the user interface to get.
	:return: The user interface with the specified identity, or None if no user
		interface with the specified identity exists.
	"""
	if identity not in _user_interfaces:
		return None
	return _user_interfaces[identity]

def register(identity, metadata):
	"""
	Registers a new user interface plug-in to communicate to the user with.

	This expects the metadata to already be verified as a user interface's
	metadata.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of the user interface plug-in.
	"""
	if identity in _user_interfaces:
		luna.plugins.api("logger").warning("User interface {user_interface} is already registered.", user_interface=identity)
		return
	_user_interfaces[identity] = _UserInterface( #Put all user interface functions in a named tuple for easier access.
		join=metadata["userinterface"]["join"],
		start=metadata["userinterface"]["start"],
		stop=metadata["userinterface"]["stop"]
	)

def validate_metadata(metadata):
	"""
	Validates whether the specified metadata is valid for user interface
	plug-ins.

	User interface metadata must have a ``userinterface`` entry, which must
	contain three entries: ``join``, ``start`` and ``stop``. These entries must
	contain callable objects (such as functions).

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "userinterface" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a user interface plug-in.")
	required_functions = {"join", "start", "stop"}
	try:
		if not required_functions <= metadata["userinterface"].keys():
			raise luna.plugins.MetadataValidationError("The user interface specifies no functions {function_names}.".format(function_names=", ".join(required_functions - metadata["userinterface"].keys())))
		for function_name in required_functions:
			if not callable(metadata["userinterface"][function_name]): #Each must be a callable object (such as a function).
				raise luna.plugins.MetadataValidationError("The {function_name} metadata entry is not callable.".format(function_name=function_name))
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The user interface metadata is not a dictionary.")