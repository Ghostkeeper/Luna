#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

cmake_minimum_required(VERSION 2.8)
project(LunaReal)

if(BUILD_TESTING)
	get_filename_component(PARENT_DIR ${PROJECT_SOURCE_DIR} DIRECTORY)
	add_test(NAME real.real_number COMMAND ${PYTHON_EXECUTABLE} -m unittest real.test.test_real_number WORKING_DIRECTORY ${PARENT_DIR})
	set_tests_properties(real.real_number PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
endif(BUILD_TESTING)