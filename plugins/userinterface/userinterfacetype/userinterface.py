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
An API for managing the user interfaces.

This allows for launching and stopping user interfaces.
"""

import userinterfacetype.userinterfaceregistrar #To get the user interface plug-ins.
import luna.plugins #To log messages.

_running = set() #Set of user interfaces that are currently running, by identity.

def join(user_interface):
	"""
	Blocks the current thread until the specified user interface has stopped.

	:param user_interface: The identity of the user interface to wait for.
	"""
	user_interface_object = userinterfacetype.userinterfaceregistrar.get_user_interface(user_interface)
	if not user_interface_object:
		luna.plugins.api("logger").warning("There is no user interface \"{plugin}\" to wait for.", plugin=user_interface)
		return
	if user_interface not in _running:
		luna.plugins.api("logger").warning("The user interface \"{plugin}\" is not running.", plugin=user_interface)
		return
	user_interface_object.join()
	_running.remove(user_interface)

def start(user_interface):
	"""
	Launches a new instance of the specified user interface.

	Only one instance of a specific plug-in may be run at the same time.
	Starting the same interface again will have no effect.

	:param user_interface: The plug-in identity of a user interface to run.
	"""
	if user_interface in _running:
		luna.plugins.api("logger").warning("User interface \"{plugin}\" is already running.", plugin=user_interface)
		return
	user_interface_object = userinterfacetype.userinterfaceregistrar.get_user_interface(user_interface)
	if not user_interface_object:
		luna.plugins.api("logger").error("There is no user interface \"{plugin}\" to launch.", plugin=user_interface)
		return

	#Checks complete. Run the interface.
	_running.add(user_interface)
	user_interface_object.start()

def stop_all():
	"""
	Stops all user interfaces that are still running.
	"""
	for user_interface, user_interface_object in userinterfacetype.userinterfaceregistrar.get_all_user_interfaces().items():
		user_interface_object.stop()
		_running.remove(user_interface)