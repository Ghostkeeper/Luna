#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_PYLINT "Build the PyLint dependency from source. If you build this, the newly-built version will get used by Luna. If not, it will search for a pre-installed version on your system." FALSE)

if(BUILD_PYLINT)
	if(NOT PYLINT_FOUND)
		message(STATUS "Building PyLint from source.")
		include(ExternalProject)
		find_package(PythonInterp 3.4.0 REQUIRED)
		ExternalProject_Add(PyLint
			URL https://pypi.python.org/packages/4e/4b/2f14a233e6c86bbfff9568d3357860573dea51be7c96eecab9471ab6ca6f/pylint-1.6.4.tar.gz#md5=66ba9c27e067568bdabcdd7c21303903
			URL_HASH SHA512=8252A46F8A7FF6A70F2EA10A94A9E8618A903014210CF87C061E649FBE0C2106FB1B63643605AE0ED3F4652E8ED09442F4FD32A0DF11F3639E6E35128E432D51
			CONFIGURE_COMMAND ""
			BUILD_COMMAND ${PYTHON_EXECUTABLE} setup.py build
			INSTALL_COMMAND ${PYTHON_EXECUTABLE} setup.py install
			BUILD_IN_SOURCE 1
		)
		set(PYLINT_FOUND TRUE)
	endif()
else() #Just find it on the system.
	include(${CMAKE_SOURCE_DIR}/cmake/FindPythonModule.cmake)
	if(ARGC GREATER 1 AND ARGV1 STREQUAL "REQUIRED")
		find_python_module(pylint REQUIRED)
	else()
		find_python_module(pylint)
	endif()
endif()