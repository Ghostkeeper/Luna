#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides a base class for the application, and then starts the application.
"""

import os #For finding the root directory of Luna.
import sys #For reading command line arguments.
import luna.plugins #To initiate the plug-in loading and use the APIs.

class Luna:
	"""
	Base instance of the application.
	"""

	DEFAULT_USER_INTERFACE = "automatic"
	"""
	The default user interface to start with, unless instructed otherwise.

	If this user interface does not exist, an error is thrown and the
	application closes.
	"""

	def run(self):
		"""
		Starts the application.

		This process will start the plug-in registering, and then selects a user
		interface based on the command line arguments.

		:returns: ``True`` if the application was finished successfully, or
			``False`` if something went wrong.
		"""
		base_dir = os.path.dirname(os.path.abspath(__file__)) #Add the plugin directories.
		luna.plugins.add_plugin_location(os.path.join(base_dir, "plugins"))
		luna.plugins.discover()
		logger = luna.plugins.api("logger")
		logger.set_levels([logger.Level.ERROR, logger.Level.CRITICAL, logger.Level.WARNING, logger.Level.INFO, logger.Level.DEBUG])

		user_interface_name = self.DEFAULT_USER_INTERFACE
		if len(sys.argv) >= 2:
			user_interface_name = sys.argv[1]
		try:
			luna.plugins.api("userinterface").start(user_interface_name)
			luna.plugins.api("userinterface").join(user_interface_name)
		except ImportError:
			logger.error("Could not load the user interface plug-in type. Aborting.")
		except:
			logger.error("A fatal error occurred. Luna must close.")
			return False
		return True #Success.

#Launches Luna if called from the command line.
if __name__ == "__main__":
	_application = Luna()
	_application.run()