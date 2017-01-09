#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
An API for using the MIME type system.

This API helps list the MIME types available to the application.
"""

import luna.plugins #To get the list of MIME plug-ins.

def all_extensions():
	"""
	Gives a sequence of all extensions we have MIME types for.
	:return: A sequence of all extensions we have MIME types for.
	"""
	for mime_plugin in luna.plugins.plugins_by_type["mime"]:
		if "extensions" in mime_plugin["mime"]:
			yield from mime_plugin["mime"]["extensions"]