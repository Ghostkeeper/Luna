#!/usr/bin/env python

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
This package contains the inner workings of Luna.

The core is kept as small as possible. Its main function is to manage the global
system that must be common knowledge across all plug-ins. This includes the
plug-in API itself, but could also include things like the internationalisation
system in the future.
"""