#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Implements the user interface plug-in interface.
"""

import luna.plugins #To get the interface we must implement and access to the logging API.

class Automatic:
	"""
	A user interface that allows no control by the user.

	This user interface is designed to work without any user input. It
	automatically converts any files in the same folder it can to the output
	files using the default settings.
	"""

	instance = None
	"""
	The instance of this user interface.

	Only one instance of this interface can exist at a time, but it is not a
	singleton. This instance gets recreated every time the interface is started,
	in order to force the user interface to lose any state it may have kept.
	"""

	def __init__(self):
		"""
		Creates a new instance of the Automatic user interface.
		"""
		super().__init__()

	def start(self):
		"""
		Starts the Automatic interface.

		For now this just prints a message that the Automatic interface is
		started.
		"""
		luna.plugins.api("logger").info("Starting Automatic interface.") #Not implemented yet.

def join():
	"""
	Blocks the current thread until the user interface has stopped.
	"""
	pass #This user interface is single-threaded, so if the start function is ran, it joins immediately.

def start():
	"""
	Starts the user interface.

	For this automatic user interface, this runs the entire program automatically.
	"""
	Automatic.instance = Automatic()
	Automatic.instance.start()

def stop():
	"""
	Stops the user interface.
	"""
	pass #This user interface is single-threaded, so if the start function is ran, it stops immediately.