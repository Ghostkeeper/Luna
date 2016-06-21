cmake_minimum_required(VERSION 2.6)
project(Luna)

#Dependencies.
find_package(PythonInterp 3.4.0 REQUIRED)

#Finding/requiring Python modules.
function(find_python_module module)
	string(TOUPPER ${module} module_normalised)
	if(NOT PY_${module_normalised})
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
			set(PY_${module_normalised} ${_${module}_location} CACHE FILEPATH "Location of Python module ${module}")
		endif(NOT _${module}_status)
	endif(NOT PY_${module_normalised})
	find_package_handle_standard_args(PY_${module} DEFAULT_MSG PY_${module_normalised})
endfunction(find_python_module)

#Tests
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
if(BUILD_TESTING)
	enable_testing()

	#Code style validation test.
	find_python_module(pylint REQUIRED)
	file(GLOB_RECURSE python_files *.py)
	add_test(NAME CodeStyleValidation COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylintrc ${python_files})
endif(BUILD_TESTING)