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

#-----------------------------Global Dependencies-------------------------------
find_package(Python REQUIRED)

#-----------------------------Plug-in Directories-------------------------------
#We need a list of these directories at multiple places, so get them here for convenience.
set(PLUGIN_DIRECTORIES "")
file(GLOB_RECURSE PLUGIN_INIT_FILES __init__.py) #All directories with __init__.py files.
foreach(INIT_FILE ${PLUGIN_INIT_FILES})
	string(FIND ${INIT_FILE} ${CMAKE_BINARY_DIR} IS_IN_BUILD_DIR)
	if(NOT ${IS_IN_BUILD_DIR} EQUAL -1)
		list(REMOVE_ITEM PLUGIN_INIT_FILES ${INIT_FILE}) #Exclude files in the build directory.
	else()
		get_filename_component(PACKAGE_DIR ${INIT_FILE} DIRECTORY) #Get directory containing the __init__.py file.
		list(APPEND PLUGIN_DIRECTORIES ${PACKAGE_DIR})
	endif()
endforeach()

#------------------------------------Tests--------------------------------------
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
if(BUILD_TESTING)
	enable_testing()

	#Code style validation.
	find_package(PyLint REQUIRED)
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
		endforeach()
	endforeach()
endif()

#--------------------------------Documentation----------------------------------
option(BUILD_DOCUMENTATION "Generate the documentation." TRUE)
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
	endforeach()

	add_custom_target(documentation ALL
		COMMAND ${CMAKE_COMMAND} -E copy_directory "${CMAKE_SOURCE_DIR}/documentation" "${DOCUMENTATION_TEMP_DIR}" &&
		${DOCUMENTATION_COPY_SOURCES_COMMANDS}
		${DOCUMENTATION_APIDOC_COMMANDS}
		${SPHINX_EXECUTABLE} -c ${CMAKE_BINARY_DIR} -n "${DOCUMENTATION_TEMP_DIR}" "${DOCUMENTATION_OUTPUT_DIR}" COMMENT "Generate documentation of the application."
	)
endif()