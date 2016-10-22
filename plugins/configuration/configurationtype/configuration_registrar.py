#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import luna.plugins #To log messages, and raise a MetadataValidationError if the metadata is invalid.

_configurations = {}
"""
The configuration classes that have been registered here so far, keyed by their
identities.
"""

def register(identity, metadata):
	"""
	Registers a new configuration plug-in to track configuration with.

	This expects the metadata to already be verified as configuration's
	metadata.

	:param identity: The identity of the plug-in to register.
	:param metadata: The metadata of a configuration plug-in.
	"""
	if identity in _configurations:
		luna.plugins.api("logger").warning("Configuration {configuration} is already registered.", configuration=identity)
		return
	_configurations[identity] = metadata["configuration"]["class"]

def unregister(identity):
	"""
	Undoes the registration of a configuration plug-in.

	The configuration plug-in will no longer keep track of any configuration.
	Existing configuration will be stored persistently.

	:param identity: The identity of the plug-in to unregister.
	"""
	if identity not in _configurations:
		luna.plugins.api("logger").warning("Configuration {configuration} is not registered, so I can't unregister it.", configuration=identity)
		return
	del _configurations[identity] #The actual unregistration.

def validate_metadata(metadata):
	if "configuration" not in metadata:
		raise luna.plugins.MetadataValidationError("This is not a configuration plug-in.")

	if "name" not in metadata:
		raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify a name.")

	if "instance" not in metadata:
		raise luna.plugins.MetadataValidationError("The configuration plug-in doesn't specify an instance to keep track of the configuration.")
	if not isinstance(metadata["instance"], configurationtype.configuration_base.ConfigurationBase):
		raise luna.plugins.MetadataValidationError("The configuration instance is not a subclass of ConfigurationBase.")