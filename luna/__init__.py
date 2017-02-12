#!/usr/bin/env python
#-*- coding: utf-8 -*-

#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

"""
This package contains the inner workings of Luna.

The core is kept as small as possible. Its main function is to manage the global
system that must be common knowledge across all plug-ins. This includes the
plug-in API itself, but could also include things like the internationalisation
system in the future.
"""

application_author = "${LUNA_AUTHOR}".replace("$" + "{LUNA_AUTHOR}", "Ghostkeeper")
"""
The author(s) of the application.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""

application_description = "${LUNA_DESCRIPTION}".replace("$" + "{LUNA_DESCRIPTION}", "Pluggable application framework.")
"""
A description for the application.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""

application_name = "${LUNA_TITLE}".replace("$" + "{LUNA_TITLE}", "Luna")
"""
The name of the application.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""

application_version_major = int("${LUNA_VERSION_MAJOR}".replace("$" + "{LUNA_VERSION_MAJOR}", "0"))
"""
The major version number of the application.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""

application_version_minor = int("${LUNA_VERSION_MINOR}".replace("$" + "{LUNA_VERSION_MINOR}", "0"))
"""
The minor version number of the application, beneath the major version.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""

application_version_patch = int("${LUNA_VERSION_PATCH}".replace("$" + "{LUNA_VERSION_PATCH}", "0"))
"""
The patch version number of the application, beneath the minor version.

This is constructed in such a way that it can be formatted by CMake if necessary
and still have a default filled in by Python if CMake wasn't applied.
"""