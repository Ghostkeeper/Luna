#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_PYTHON "Build the Python dependency from source. If you build this, the newly-built version will get used by Luna. If not, it will search for a pre-installed version on your system." FALSE)

if(BUILD_PYTHON)
	if(WIN32)
		message(WARNING "Building Python on Windows is not supported at the moment. You will probably run into problems.")
	endif(WIN32)
	ExternalProject_Add(Python
		URL https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
		URL_HASH SHA512=248B3EF2DEFEE7C013E8AC7472B9F2828B1C5B07A2F091EAD46EBDF209BE11DD37911978B590367699D9FAD50F1B98B998BCEEC34FA8369BA30950D3A5FB596F
		CONFIGURE_COMMAND ./configure --prefix=${CMAKE_INSTALL_PREFIX} --enable-shared --with-threads
		BUILD_IN_SOURCE 1
	)
	set(PYTHON_EXECUTABLE ${CMAKE_INSTALL_PREFIX}/bin/python3)
	set(PYTHON_FOUND TRUE)
else(BUILD_PYTHON) #Just find it on the system.
	if(ARGC GREATER 1 AND ARGV1 STREQUAL "REQUIRED") #Pass the REQUIRED parameter on to the script. Perhaps also do other parameters?
		find_package(PythonInterp 3.4.0 REQUIRED)
	else()
		find_package(PythonInterp 3.4.0)
	endif()
	if(PYTHONINTERP_FOUND) #Rename this variable to our own conventions.
		set(PYTHON_FOUND TRUE)
	endif()
endif(BUILD_PYTHON)