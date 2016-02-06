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

from Luna.Logger import Logger,Level
import datetime #For putting timestamps alongside each message.
import ctypes #For printing in colour on Windows machines.

#Logs messages to the standard output of the program.
class StandardOut(Logger):
	#Creates a new instance of the StandardOut logger.
	def __init__(self):
		Logger.__init__(self)
		self.__standardOutHandle = None
		if ctypes and ctypes.windll and ctypes.windll.kernel32: #Windows bash.
			self.__standardOutHandle = ctypes.windll.kernel32.GetStdHandle(-11) #-11 is the flag for standard output in the Windows API.
			self.__defaultConsoleAttributes = ctypes.windll.kernel32.GetConsoleScreenBufferInfo(-11)

	#Logs a new message.
	#
	#A timestamp is logged alongside with the logged message.
	def log(self,level,message,*arguments):
		formatted = datetime.datetime.strftime(datetime.datetime.now(),"[%H:%M:%S] ") #Format the date and time.
		formatted += message % arguments #Replace the %'s in the message with the arguments.
		if ctypes and ctypes.windll and ctypes.windll.kernel32: #Windows bash.
			self.colourPrintWin32(formatted,level)
		else:
			self.colourPrintAnsi(formatted,level)

	#Prints a message with colour-coding in Windows Bash.
	#
	#The colour coding is based on the level of the message:
	# - Red for errors.
	# - Magenta for criticals.
	# - Yellow for warnings.
	# - Green for information.
	# - Blue for debug messages.
	#
	#\param message The text to print.
	#\param level The warning level of the message.
	def colourPrintWin32(self,message,level):
		if level == Level.ERROR:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,12) #Red.
		elif level == Level.CRITICAL:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,13) #Magenta.
		elif level == Level.WARNING:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,14) #Yellow.
		elif level == Level.INFO:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,10) #Green.
		elif level == Level.DEBUG:
			ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,9) #Blue.
		print(message)
		ctypes.windll.kernel32.SetConsoleTextAttribute(self.__standardOutHandle,15) #Reset to white. TODO: The default is not always white!

	#Prints a message with colour-coding in ANSI-based terminals, such as Linux.
	#
	#The colour coding is based on the level of the message:
	# - Red for errors.
	# - Magenta for criticals.
	# - Yellow for warnings.
	# - Green for information.
	# - Blue for debug messages.
	#
	#\param message The text to print.
	#\param level The warning level of the message.
	def colourPrintAnsi(self,message,level):
		if level == Level.ERROR:
			ansiColour = '\033[38m' #Red.
		elif level == Level.CRITICAL:
			ansiColour = '\033[35m' #Magenta.
		elif level == Level.WARNING:
			ansiColour = '\033[33m' #Yellow.
		elif level == Level.INFO:
			ansiColour = '\033[32m' #Green.
		elif level == Level.DEBUG:
			ansiColour = '\033[34m' #Blue.
		print(ansiColour + message + '\033[m') #Start code, then message, then revert to default colour.