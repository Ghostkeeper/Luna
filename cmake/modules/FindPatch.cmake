#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_PATCH "Build the Patch dependency from source. If you build this, the newly-built version will get used by Luna. If not, it will search for a pre-installed version on your system." FALSE)

if(BUILD_PATCH)
	if(NOT PATCH_FOUND)
		message(STATUS "Building Patch from source.")
		include(ExternalProject)
		ExternalProject_Add(Patch
			URL http://downloads.sourceforge.net/project/unxutils/unxutils/current/UnxUtilsSrc.zip
			URL_HASH SHA512=771910CE864BBDAA9351534DBF5F8CAE8B5CB9336704CF4948B2E5F9FF4614FD1DE68A313EBD8450D7973BFF1E62DE1CA16E96AC610E0679B5139B4C154E09C9
			CONFIGURE_COMMAND ""
			BUILD_COMMAND ${CMAKE_MAKE_PROGRAM} -C ./patch-2.5 #Call make from the patch-2.5 subdirectory.
			INSTALL_COMMAND ""
			BUILD_IN_SOURCE 1
		)
		set(PATCH_EXECUTABLE patch)
		set(PATCH_FOUND TRUE)
	endif()
else() #Just find it on the system.
	include(FindPackageHandleStandardArgs)
	find_program(PATCH_EXECUTABLE NAMES patch PATH_SUFFIXES bin DOC "Application to apply unified diff format patches.")
	find_package_handle_standard_args(Patch DEFAULT_MSG PATCH_EXECUTABLE)
endif()