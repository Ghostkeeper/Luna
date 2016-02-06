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

import importlib.util #Imports Python modules dynamically.
import os #To search through folders to find the plug-ins.
import pkgutil #Imports Python packages dynamically.

#Handles all administration on plug-ins.
#
#Note that this class is completely static. This is by design. There should
#never be multiple instances of this class, and having an interface for it makes
#no sense.
#
#Since this class comes in effect before any logging is available, it may never
#log anything. The philosophy of this class should therefore be to gracefully
#degrade if anything goes wrong, always check input, and especially to leave the
#error handling to other classes.
class Plugins:
	#Version number of the plug-in API.
	#
	#Each plug-in carries a similar version number which determines the minimum
	#API version required of Luna to function. If this version number is lower
	#than the version number in the plug-in, the plug-in is not loaded.
	APIVERSION = 1

	#List of directories where to look for plug-ins.
	__pluginLocations = []

	#Dictionary holding all plug-ins.
	#
	#The plug-ins are indexed by a key of the form "<type>/<name>", indicating
	#the type and the name of the plug-in.
	__plugins = {}

	#Adds a location to the list of locations where the application looks for
	#plug-ins.
	#
	#\param location The location to add to the location list.
	def addPluginLocation(location):
		if location:
			Plugins.__pluginLocations.append(location)

	#Discovers all plug-ins it can find.
	#
	#This goes through all folders of all plug-in types, and finds out what
	#their metadata is. If the metadata is correct it will create a plug-in.
	#When all plug-ins are loaded, the plug-ins whose dependencies can be met
	#will be stored for later requesting. The plug-ins whose dependencies cannot
	#be met will be discarded.
	#This method can also be used to update the plug-in repository, but plug-ins
	#are not deleted then. Only new plug-ins are added by this function.
	def discover():
		candidates = [] #Plug-ins we've found here. Dependencies are not checked yet when they enter this list.
		pluginPaths = Plugins.__findPluginPaths()
		for pluginPath in pluginPaths:
			module = Plugins.__createPackage(pluginPath)
			if not module: #Module loading failed.
				continue

			#Reading the metadata.
			try:
				metadata = module.metadata()
			except: #Error in metadata()
				continue
			if not isinstance(metadata,dict): #Metadata didn't return a dictionary.
				continue
			if not "api" in metadata or metadata["api"] > Plugins.APIVERSION: #Plug-in requires newer version of Luna to interface.
				continue
			if not "type" in metadata:
				continue
			pluginType = metadata["type"]
			if not "class" in metadata:
				continue
			pluginClass = metadata["class"]
			_,name = os.path.split(pluginPath) #Get the name of the plug-in from the directory name.
			dependencies = [] #If this entry is missing, assume there are no dependencies.
			if "dependencies" in metadata:
				dependencies = metadata["dependencies"]

			#Creating the plug-in instance.
			try:
				plugin = pluginClass() #Run the constructor of the plug-in class!
			except: #Plug-in constructor gave an exception.
				continue
			plugin.name = name
			plugin.type = pluginType
			plugin.dependencies = dependencies
			candidates.append(plugin)

		#Now go through the list and add all plug-ins whose dependencies can be met.
		for plugin in candidates:
			for dependency in plugin.dependencies:
				if "/" not in dependency: #Dependency syntax in plug-in metadata is wrong.
					break
				dependencyType,dependencyName = dependency.split("/",1) #Parse the dependency.
				for candidate in candidates:
					if candidate.type == dependencyType and candidate.name == dependencyName: #Found the dependency.
						break
				else: #Dependency was not found.
					break
			else: #All dependencies are present.
				Plugins.__plugins[plugin.type + "/" + plugin.name] = plugin #Actually add the plug-in!

		importlib.invalidate_caches() #Updates cached versions of the packages.

	#Gets an interface plug-in with the specified name, if it exists.
	#
	#\param name The name of the interface plug-in to get.
	#\return The specified interface, or None if it doesn't exist.
	def getInterface(name):
		return Plugins.__getPlugin("Interface",name)

	#Gets a logger plug-in with the specified name, if it exists.
	#
	#\param name The name of the logger plug-in to get.
	#\return The specified logger, or None if it doesn't exist.
	def getLogger(name):
		return Plugins.__getPlugin("Logger",name)

	#Creates a package out of the specified plug-in path.
	#
	#The path should already be known to contain __init__.py. This function does
	#two things under water: It loads all modules in the specified folder, and
	#it creates an additional model for __init__.py and executes that model. The
	#init script's model is returned so that the metadata can be requested from
	#that script later.
	#
	#\param pluginPath The path to the plug-in's folder.
	#\return A Python module created from the init script in the specified
	#folder, or None if loading failed.
	def __createPackage(pluginPath):
		#Create a package from all modules in the plugin folder.
		for importer,packageName,_ in pkgutil.iter_modules([pluginPath]):
			module = importer.find_module(packageName).load_module(packageName)

		#Create a module from __init__.py
		_,packageName = os.path.split(pluginPath)
		try:
			spec = importlib.util.spec_from_file_location(packageName,os.path.join(pluginPath,"__init__.py"))
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)
		except: #Any number of reasons: No __init__.py, syntax error, dependency not mentioned, etc.
			return None
		return module

	#Creates a list of paths to folders of candidate plug-ins.
	#
	#These candidates are plug-ins that might be loaded as a real plug-in at
	#some point, but whether this is possible is not certain yet because the
	#metadata has not yet been looked at.
	#
	#\return A list of paths to plug-in folders.
	def __findPluginPaths():
		candidates = []
		for location in Plugins.__pluginLocations:
			if not os.path.isdir(location): #Invalid plug-in location.
				continue
			for pluginFolder in os.listdir(location):
				pluginFolder = os.path.join(location,pluginFolder)
				if not os.path.isdir(pluginFolder): #os.listdir gets both files and folders. We want only folders at this level.
					continue
				initScript = os.path.join(pluginFolder,"__init__.py") #Plug-in must have an init script.
				if os.path.exists(initScript) and (os.path.isfile(initScript) or os.path.islink(initScript)):
					candidates.append(pluginFolder)
		return candidates

	#Gets a plug-in of the specified type and the specified name, if it exists.
	#
	#\param type The plug-in type of the plug-in to get.
	#\param name The name of the plug-in to get.
	#\return The plug-in, or None if it doesn't exist.
	def __getPlugin(type,name):
		id = type + "/" + name
		if id in Plugins.__plugins:
			return Plugins.__plugins[id]
		return None #Plug-in couldn't be found.