#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

cmake_minimum_required(VERSION 3.2.3)
project(Luna)
include(${CMAKE_SOURCE_DIR}/cmake/GetMIMETypes.cmake)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake/modules")

#----------------------------Application Metadata-------------------------------
set(LUNA_TITLE "Luna" CACHE STRING "Application title.")
set(LUNA_AUTHOR "Ghostkeeper" CACHE STRING "Author of the application.")
set(LUNA_DESCRIPTION "Conversion application." CACHE STRING "Description of the application.")
set(LUNA_VERSION_MAJOR 0 CACHE STRING "Major version number. The major version number must increase for every release that alters any pre-existing API.")
set(LUNA_VERSION_MINOR 0 CACHE STRING "Minor version number. The minor version number must increase for every release that introduces new features and does not alter any pre-existing API.")
set(LUNA_VERSION_PATCH 0 CACHE STRING "Patch version number. The patch version number must increase for every release that only fixes bugs and does not alter any pre-existing API.")

#----------------------------------File Lists-----------------------------------
set(PYTHON_FILES_RELATIVE #Used to find files for linting, and to find plug-ins without having to use GLOB.
	__main__.py
	luna/__init__.py
	luna/model.py
	luna/plugins.py
	luna/tests.py
	plugins/configuration/configurationtype/__init__.py
	plugins/configuration/configurationtype/configuration.py
	plugins/configuration/configurationtype/configuration_error.py
	plugins/configuration/configurationtype/test/test_init.py
	plugins/data/datatype/__init__.py
	plugins/data/datatype/data.py
	plugins/data/datatype/test/test_init.py
	plugins/logger/loggertype/__init__.py
	plugins/logger/loggertype/log.py
	plugins/logger/loggertype/test/test_init.py
	plugins/logger/standardout/__init__.py
	plugins/logger/standardout/buffer_info.py
	plugins/logger/standardout/c_type_coordinate.py
	plugins/logger/standardout/c_type_rectangle.py
	plugins/logger/standardout/standard_out.py
	plugins/logger/standardout/test/test_standard_out.py
	plugins/mime/mimetype/__init__.py
	plugins/mime/mimetype/mime.py
	plugins/mime/mimetype/test/test_init.py
	plugins/storage/localstorage/__init__.py
	plugins/storage/localstorage/atomic_write_stream.py
	plugins/storage/localstorage/local_storage.py
	plugins/storage/localstorage/test/test_local_storage.py
	plugins/storage/storagetype/__init__.py
	plugins/storage/storagetype/storage.py
	plugins/storage/storagetype/test/test_init.py
	plugins/storage/storagetype/test/test_integration.py
	plugins/userinterface/automatic/__init__.py
	plugins/userinterface/automatic/automatic.py
	plugins/userinterface/automatic/state.py
	plugins/userinterface/userinterfacetype/__init__.py
	plugins/userinterface/userinterfacetype/test/test_init.py
	plugins/userinterface/userinterfacetype/user_interface.py
)
set(PYTHON_FILES "")
foreach(PYTHON_FILE_RELATIVE ${PYTHON_FILES_RELATIVE})
	list(APPEND PYTHON_FILES ${CMAKE_SOURCE_DIR}/${PYTHON_FILE_RELATIVE})
endforeach()

#-----------------------------Global Dependencies-------------------------------
find_package(Python REQUIRED)

#------------------------------------Tests--------------------------------------
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
if(BUILD_TESTING)
	enable_testing()

	#Code style validation.
	find_package(PyLint REQUIRED)
	configure_file("${CMAKE_SOURCE_DIR}/pylintrc.in" "${CMAKE_BINARY_DIR}/pylintrc")
	add_test(NAME CodeStyle COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_BINARY_DIR}/pylintrc ${PYTHON_FILES})
	set_tests_properties(CodeStyle PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
endif()

#-----------------------------Plug-in Directories-------------------------------
#Execute the CMakeLists of every plug-in that has one.
#We need a list of these directories at multiple places, so get them here for convenience.
set(PLUGIN_DIRECTORIES "")
set(MIME_TYPES "") #MIME types.
set(MIME_EXTENSIONS "") #Extensions for each MIME type.
set(MIME_NAMES "") #Human-readable names for each MIME type.
foreach(PYTHON_FILE ${PYTHON_FILES})
	string(FIND ${PYTHON_FILE} "/__init__.py" IS_INIT_FILE)
	if(NOT ${IS_INIT_FILE} EQUAL -1) #Contains the string "/__init__.py". Let's assume this is the file name.
		get_filename_component(PACKAGE_DIR ${PYTHON_FILE} DIRECTORY) #Get directory containing the __init__.py file.
		if(EXISTS ${PACKAGE_DIR}/CMakeLists.txt)
			add_subdirectory(${PACKAGE_DIR})
		endif()
		list(APPEND PLUGIN_DIRECTORIES ${PACKAGE_DIR})
		get_mime_types(${PACKAGE_DIR})
	endif()
endforeach()
message(STATUS "Found these MIME types: ${MIME_TYPES}")

#--------------------------------Documentation----------------------------------
option(BUILD_DOCUMENTATION "Generate the documentation." TRUE)
if(BUILD_DOCUMENTATION)
	find_package(Sphinx 1.4.0 REQUIRED)
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