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
Provides a base class for the application, and then starts the application.
"""

import os #For finding the root directory of Luna.
import sys #For reading command line arguments.
import Luna.Logger as Logger
import Luna.Plugins as Plugins #To initiate the plug-in loading.

class Luna(object):
	"""
	Base instance of the application.
	"""

	def run(self):
		"""
		.. function:: run()
		Starts the application.

		This process will start the plug-in registering, and then selects an
		interface based on the command line arguments.

		:returns: ``True`` if the application was finished successfully, or ``False`` if something went wrong.
		"""
		baseDir = os.path.dirname(os.path.abspath(__file__)) #Add the plugin directories.
		Plugins.Plugins.addPluginLocation(os.path.join(baseDir,"Interface"))
		Plugins.Plugins.addPluginLocation(os.path.join(baseDir,"Logger"))
		Plugins.Plugins.discover()
		Logger.Logger.setLogLevels([Logger.Level.ERROR,Logger.Level.CRITICAL,Logger.Level.WARNING,Logger.Level.INFO,Logger.Level.DEBUG])

		interfaceName = "Automatic" #Default to Automatic interface.
		if len(sys.argv) >= 2:
			interfaceName = sys.argv[1]
		interface = Plugins.Plugins.getInterface(interfaceName)
		if not interface:
			Logger.Logger.error("Could not load the interface %s. Aborting.",interfaceName)
			return False
		interface.start()

		return True #Success.

#Launches Luna if called from the command line.
if __name__ == "__main__":
	application = Luna()
	application.run()