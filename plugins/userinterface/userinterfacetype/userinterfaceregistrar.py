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
Keeps track of all user interface plug-ins.

User interface plug-ins need to register here. Their implementations are stored
and may be called upon to start and communicate with the user interface.
"""

import luna.plugins #To raise a MetadataValidationError if the metadata is invalid.
import userinterfacetype.userinterfaceinterface #To check if a user interface implements the user interface interface.

__userinterfaces = {}
"""
The user interfaces that have been registered here so far, keyed by their
identities.
"""

def get_all_user_interfaces():
	"""
	.. function:: get_all_user_interfaces()
	Gets all user interfaces that have been registered here so far.

	:return: A generator of user interfaces.
	"""
	return __userinterfaces.values()

def get_user_interface(identity):
	"""
	.. function:: get_user_interface(identity)
	Gets a specific user interface plug-in object by identity.

	:param identity: The identity of the user interface to get.
	:return: The user interface with the specified identity, or None if no user
		interface with the specified identity exists.
	"""

def register(identity, metadata):
	"""
	.. function:: register(identity, metadata)
	Registers a new user interface plug-in to communicate to the user with.

	This expects the metadata to already be verified as a user interface's
	metadata.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of the user interface plug-in.
	"""
	if identity in __userinterfaces:
		return
	__userinterfaces[identity] = metadata["userinterface"]["implementation"]()

def validate_metadata(metadata):
	"""
	.. function:: validate_metadata(metadata)
	Validates whether the specified metadata is valid for user interface
	plug-ins.

	User interface metadata must have a "userinterface" field, which contains an
	"implementation" field. This field must contain a class which inherits from
	the UserInterfaceInterface interface.

	:param metadata: The metadata to validate.
	:raises luna.plugins.MetadataValidationError: The metadata was invalid.
	"""
	if "userinterface" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a user interface plug-in.")
	required_fields = {"implementation"}
	try:
		if not required_fields <= metadata["userinterface"].keys():
			raise luna.plugins.MetadataValidationError("The user interface specifies no implementation.")
		if not issubclass(metadata["userinterface"]["implementation"], userinterfacetype.userinterfaceinterface.UserInterfaceInterface):
			raise luna.plugins.MetadataValidationError("The user interface is not implemented by the provided plug-in.")
	except (AttributeError, TypeError): #Not a dictionary.
		raise luna.plugins.MetadataValidationError("The user interface metadata is not a dictionary.")