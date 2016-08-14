#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

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