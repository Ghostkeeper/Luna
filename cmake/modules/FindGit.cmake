#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_GIT "Build the Git dependency from source. If you build this, the newly-built version will get used by Luna. If not, it will search for a pre-installed version on your system." FALSE)

if(BUILD_GIT)
	if(NOT GIT_FOUND)
		message(STATUS "Building Git from source.")
		include(ExternalProject)
		ExternalProject_Add(Git
			URL https://www.kernel.org/pub/software/scm/git/git-2.10.0.tar.gz
			URL_HASH SHA512=EA6312A5F3EC3DBC48E02F65798A4EA8B5CAB60CC0D9DA6EF4A32A575324C12617F76604E4AD5DA9835F0F6769F405526133E831B327262B67A070EEFCDEDDEA
			CONFIGURE_COMMAND "" #No CMakeLists here.
		)
		set(GIT_EXECUTABLE ${CMAKE_CURRENT_BINARY_DIR}/Git-prefix/src/Git-build/git)
		set(git_version "git version 2.10.0")
		set(GIT_VERSION_STRING "2.10.0")
		function(_ep_get_git_version git_EXECUTABLE git_version_var) #Overwrite the function in ExternalProject that gets the Git version, since it can't call Git before it's built.
			set(${git_version_var} "2.10.0" PARENT_SCOPE)
		endfunction()
		set(GIT_FOUND TRUE)
	endif()
else() #Just find it on the system.
	include(FindPackageHandleStandardArgs)
	find_program(GIT_EXECUTABLE NAMES git PATH_SUFFIXES bin DOC "Version control application, used to download Git repositories and apply patches.")
	find_package_handle_standard_args(Git DEFAULT_MSG GIT_EXECUTABLE)
endif()