cmake_minimum_required(VERSION 2.6)
project(Luna)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

#Dependencies.
find_package(PythonInterp 3.4.0 REQUIRED)

#Finding/requiring Python modules.
function(find_python_module module)
	string(TOUPPER ${module} module_uppercase)
	if(NOT PYTHON_${module_uppercase})
		if(ARGC GREATER 1 AND ARGV1 STREQUAL "REQUIRED")
			set(${module}_FIND_REQUIRED TRUE)
		endif()
		#Compile a bit of Python that imports the module and checks if that succeeded.
		execute_process(
			COMMAND "${PYTHON_EXECUTABLE}" "-c" "import re, ${module}; print(re.compile('/__init__.py.*').sub('', ${module}.__file__))"
			RESULT_VARIABLE _${module}_status
			OUTPUT_VARIABLE _${module}_location
			ERROR_QUIET
			OUTPUT_STRIP_TRAILING_WHITESPACE
		)
		if(NOT _${module}_status)
			set(PYTHON_${module_uppercase} ${_${module}_location} CACHE FILEPATH "Location of Python module ${module}.")
		endif(NOT _${module}_status)
	endif(NOT PYTHON_${module_uppercase})
	find_package_handle_standard_args(PYTHON_${module} DEFAULT_MSG PYTHON_${module_uppercase})
endfunction(find_python_module)

#Tests
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
if(BUILD_TESTING)
	enable_testing()

	#Code style validation.
	find_python_module(pylint REQUIRED)
	file(GLOB_RECURSE python_files *.py)
	add_test(NAME CodeStyle COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylintrc ${python_files})
	set_tests_properties(CodeStyle PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
endif(BUILD_TESTING)

#Documentation
option(BUILD_DOCUMENTATION "Generate the documentation." TRUE)
if(BUILD_DOCUMENTATION)
	find_package(Sphinx REQUIRED)
	set(DOCUMENTATION_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/documentation")
	configure_file("${CMAKE_SOURCE_DIR}/sphinx_configuration.py.in" "${CMAKE_BINARY_DIR}/sphinx_configuration.py" @ONLY)
	add_custom_target(documentation ALL ${SPHINX_EXECUTABLE} -n "${CMAKE_SOURCE_DIR}" "${DOCUMENTATION_OUTPUT_DIR}" COMMENT "Generate technical documentation of the application.")
endif(BUILD_DOCUMENTATION)
