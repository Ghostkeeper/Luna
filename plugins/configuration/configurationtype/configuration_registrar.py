#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

import luna.plugins

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
	raise Exception("Not implemented yet.")

def validate_metadata(metadata):
	raise Exception("Not implemented yet.")