#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

cmake_minimum_required(VERSION 3.2.3)
project(Luna)
include(${CMAKE_SOURCE_DIR}/cmake/FindPythonModule.cmake)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")

#----------------------------Application Metadata-------------------------------
set(LUNA_TITLE "Luna" CACHE STRING "Application title.")
set(LUNA_AUTHOR "Ghostkeeper" CACHE STRING "Author of the application.")
set(LUNA_DESCRIPTION "Conversion application." CACHE STRING "Description of the application.")
set(LUNA_VERSION_MAJOR 0 CACHE STRING "Major version number. The major version number must increase for every release that alters any pre-existing API.")
set(LUNA_VERSION_MINOR 0 CACHE STRING "Minor version number. The minor version number must increase for every release that introduces new features and does not alter any pre-existing API.")
set(LUNA_VERSION_PATCH 0 CACHE STRING "Patch version number. The patch version number must increase for every release that only fixes bugs and does not alter any pre-existing API.")

#-----------------------------Plug-in Directories-------------------------------
#We need a list of these directories at multiple places, so get them here for convenience.
set(PLUGIN_DIRECTORIES "")
file(GLOB_RECURSE PLUGIN_INIT_FILES __init__.py) #All directories with __init__.py files.
foreach(INIT_FILE ${PLUGIN_INIT_FILES})
	string(FIND ${INIT_FILE} ${CMAKE_BINARY_DIR} IS_IN_BUILD_DIR)
	if(NOT ${IS_IN_BUILD_DIR} EQUAL -1)
		list(REMOVE_ITEM PLUGIN_INIT_FILES ${INIT_FILE}) #Exclude files in the build directory.
	else(NOT ${IS_IN_BUILD_DIR} EQUAL -1)
		get_filename_component(PACKAGE_DIR ${INIT_FILE} DIRECTORY) #Get directory containing the __init__.py file.
		list(APPEND PLUGIN_DIRECTORIES ${PACKAGE_DIR})
	endif(NOT ${IS_IN_BUILD_DIR} EQUAL -1)
endforeach(INIT_FILE ${PLUGIN_INIT_FILES})

#-----------------------------------Targets-------------------------------------
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
option(BUILD_DOCUMENTATION "Generate the documentation." TRUE)
option(BUILD_MISSING_DEPENDENCIES "Dependencies that are missing should be built from source." FALSE)

#---------------------------------Dependencies----------------------------------
if(BUILD_MISSING_DEPENDENCIES)
	include(ExternalProject)
	set(DEPENDENCIES_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/inst)

	#Python.
	find_package(PythonInterp 3.4.0)
	if(NOT PYTHONINTERP_FOUND)
		option(BUILD_PYTHON "Build Python from source." TRUE)
		if(BUILD_PYTHON)
			message(STATUS "Dependency Python is missing and will be built from source.")
			if(WIN32)
				ExternalProject_Add(Python
					URL https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
					URL_HASH SHA512=248B3EF2DEFEE7C013E8AC7472B9F2828B1C5B07A2F091EAD46EBDF209BE11DD37911978B590367699D9FAD50F1B98B998BCEEC34FA8369BA30950D3A5FB596F
					CONFIGURE_COMMAND echo Skipping configure command on Windows.
					BUILD_COMMAND ./PCBuild/build.bat -e
					BUILD_IN_SOURCE 1
				)
				set(PYTHON_EXECUTABLE ${DEPENDENCIES_INSTALL_PREFIX}/bin/python3.exe)
			else(WIN32)
				ExternalProject_Add(Python
					URL https://www.python.org/ftp/python/3.5.2/Python-3.5.2.tgz
					URL_HASH SHA512=248B3EF2DEFEE7C013E8AC7472B9F2828B1C5B07A2F091EAD46EBDF209BE11DD37911978B590367699D9FAD50F1B98B998BCEEC34FA8369BA30950D3A5FB596F
					CONFIGURE_COMMAND ./configure --prefix=${DEPENDENCIES_INSTALL_PREFIX} --enable-shared --with-threads
					BUILD_IN_SOURCE 1
				)
				set(PYTHON_EXECUTABLE ${DEPENDENCIES_INSTALL_PREFIX}/bin/python3)
			endif(WIN32)
			set(PythonInterp_FOUND TRUE)
		endif(BUILD_PYTHON)
	endif(NOT PYTHONINTERP_FOUND)

	#PyLint.
	if(BUILD_TESTING) #PyLint is only required for testing.
		find_python_module(pylint)
		if(NOT PYTHON_PYLINT_FOUND)
			option(BUILD_PYLINT "Build PyLint from source." TRUE)
			if(BUILD_PYLINT)
				if(NOT PYTHON_EXECUTABLE)
					message(ERROR "Building PyLint from source requires Python.")
				endif(NOT PYTHON_EXECUTABLE)
				message(STATUS "Dependency PyLint is missing and will be built from source.")
				ExternalProject_Add(PyLint
					URL https://pypi.python.org/packages/4e/4b/2f14a233e6c86bbfff9568d3357860573dea51be7c96eecab9471ab6ca6f/pylint-1.6.4.tar.gz#md5=66ba9c27e067568bdabcdd7c21303903
					URL_HASH SHA512=8252A46F8A7FF6A70F2EA10A94A9E8618A903014210CF87C061E649FBE0C2106FB1B63643605AE0ED3F4652E8ED09442F4FD32A0DF11F3639E6E35128E432D51
					CONFIGURE_COMMAND ""
					BUILD_COMMAND ${PYTHON_EXECUTABLE} setup.py build
					INSTALL_COMMAND ${PYTHON_EXECUTABLE} setup.py install
					BUILD_IN_SOURCE 1
				)
			endif(BUILD_PYLINT)
		endif(NOT PYTHON_PYLINT_FOUND)
	endif(BUILD_TESTING)
else(BUILD_MISSING_DEPENDENCIES)
	#Python.
	find_package(PythonInterp 3.4.0 REQUIRED)
endif(BUILD_MISSING_DEPENDENCIES)

#------------------------------------Tests--------------------------------------
if(BUILD_TESTING)
	enable_testing()

	#Code style validation.
	find_python_module(pylint REQUIRED)
	configure_file("${CMAKE_SOURCE_DIR}/pylintrc.in" "${CMAKE_BINARY_DIR}/pylintrc")
	file(GLOB_RECURSE PYTHON_FILES *.py)
	add_test(NAME CodeStyle COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_BINARY_DIR}/pylintrc ${PYTHON_FILES})
	set_tests_properties(CodeStyle PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})

	#Plug-in unit tests.
	foreach(PLUGIN_DIRECTORY ${PLUGIN_DIRECTORIES})
		get_filename_component(PLUGIN_NAME ${PLUGIN_DIRECTORY} NAME)
		get_filename_component(PARENT_DIRECTORY ${PLUGIN_DIRECTORY} DIRECTORY) #Run the test from the parent directory such that all imports are correct.
		file(GLOB_RECURSE UNIT_TESTS RELATIVE ${PLUGIN_DIRECTORY} ${PLUGIN_DIRECTORY}/test/*.py)
		foreach(UNIT_TEST ${UNIT_TESTS})
			string(REGEX REPLACE "\\.py$" "" UNIT_TEST2 ${UNIT_TEST}) #Turn filename into Python module.
			string(REGEX REPLACE "\\/" "." UNIT_TEST3 ${UNIT_TEST2})
			add_test(NAME ${PLUGIN_NAME}.${UNIT_TEST3} COMMAND ${PYTHON_EXECUTABLE} -m unittest ${PLUGIN_NAME}.${UNIT_TEST3} WORKING_DIRECTORY ${PARENT_DIRECTORY})
			set_tests_properties(${PLUGIN_NAME}.${UNIT_TEST3} PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
		endforeach(UNIT_TEST ${UNIT_TESTS})
	endforeach(PLUGIN_DIRECTORY ${PLUGIN_DIRECTORIES})
endif(BUILD_TESTING)

#--------------------------------Documentation----------------------------------
if(BUILD_DOCUMENTATION)
	find_package(Sphinx REQUIRED)
	set(DOCUMENTATION_OUTPUT_DIR "${CMAKE_BINARY_DIR}/documentation" CACHE FILEPATH "Where to save generated documentation.")
	set(DOCUMENTATION_TEMP_DIR "${CMAKE_BINARY_DIR}/documentation_source")

	#Information to put in the Sphinx configuration file.
	string(TIMESTAMP DOCUMENTATION_YEAR "%Y")
	configure_file("${CMAKE_SOURCE_DIR}/sphinx_configuration.py.in" "${CMAKE_BINARY_DIR}/conf.py")

	#Get all plug-in directories.
	set(DOCUMENTATION_APIDOC_COMMANDS "")
	set(DOCUMENTATION_COPY_SOURCES_COMMANDS "")
	foreach(PLUGIN_DIRECTORY ${PLUGIN_DIRECTORIES})
		get_filename_component(PACKAGE_NAME ${PLUGIN_DIRECTORY} NAME)
		list(APPEND DOCUMENTATION_APIDOC_COMMANDS ${SPHINX_APIDOC_EXECUTABLE} -o ${DOCUMENTATION_TEMP_DIR}/technical -e ${PLUGIN_DIRECTORY} &&) #Generate the documentation.
		list(APPEND DOCUMENTATION_COPY_SOURCES_COMMANDS ${CMAKE_COMMAND} -E copy_directory "${PLUGIN_DIRECTORY}" "${DOCUMENTATION_TEMP_DIR}/${PACKAGE_NAME}" &&) #Copy sources so that any other .rst files are included.
	endforeach(PLUGIN_DIRECTORY ${PLUGIN_DIRECTORIES})

	add_custom_target(documentation ALL
		COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_SOURCE_DIR}/documentation" "${DOCUMENTATION_TEMP_DIR}" &&
		${DOCUMENTATION_COPY_SOURCES_COMMANDS}
		${DOCUMENTATION_APIDOC_COMMANDS}
		${SPHINX_EXECUTABLE} -c ${CMAKE_BINARY_DIR} -n "${DOCUMENTATION_TEMP_DIR}" "${DOCUMENTATION_OUTPUT_DIR}" COMMENT "Generate documentation of the application."
	)
endif(BUILD_DOCUMENTATION)