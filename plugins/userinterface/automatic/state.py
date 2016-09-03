#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
Provides the possible states the automatic interface can be in.

Changes to the state can be listened to and acted on.
"""

import enum #To enumerate the possible states.

class State(enum.Enum):
	"""
	Defines the possible states the automatic interface can be in.
	"""

	stopped = 0
	"""
	The state is not started, or not yet started.

	This is the initial state when the plug-in is just created. The state is
	also entered when the interface has completed running.
	"""

	started = 1
	"""
	The interface has been started externally.
	"""