cmake_minimum_required(VERSION 2.8)
project(Luna)
set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

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
	if(NOT PythonInterp_FOUND)
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
	endif(NOT PythonInterp_FOUND)

	#Sphinx.
	if(BUILD_DOCUMENTATION) #Sphinx is only required for documentation.
		find_package(Sphinx)
		if(NOT SPHINX_FOUND)
			option(BUILD_SPHINX "Build Sphinx from source." TRUE)
			if(BUILD_SPHINX)
				if(NOT PYTHON_EXECUTABLE)
					message(ERROR "Building Sphinx from source requires Python.")
				endif(NOT PYTHON_EXECUTABLE)
				message(STATUS "Depencency Sphinx is missing and will be built from source.")
				ExternalProject_Add(Sphinx
					URL https://pypi.python.org/packages/8b/78/eeea2b837f911cdc301f5f05163f9729a2381cadd03ccf35b25afe816c90/Sphinx-1.4.5.tar.gz#md5=5c2cd2dac45dfa6123d067e32a89e89a
					URL_HASH SHA512=E11CA5E02C44A2112CA31E1CFF4DB8A89AC0D58E410AEF43EAD48C74520DACAE61BA8AA5B91C5F6EF920851E35A2FF1470E74FD038CB50AC9BB6F689C495CEE7
					CONFIGURE_COMMAND ""
					BUILD_COMMAND ${PYTHON_EXECUTABLE} setup.py build
					INSTALL_COMMAND ${PYTHON_EXECUTABLE} setup.py install
					BUILD_IN_SOURCE 1
				)
				set(SPHINX_EXECUTABLE sphinx-build)
				set(SPHINX_FOUND TRUE)
			endif(BUILD_SPHINX)
		endif(NOT SPHINX_FOUND)
	endif(BUILD_DOCUMENTATION)
else(BUILD_MISSING_DEPENDENCIES)
	#Python.
	find_package(PythonInterp 3.4.0 REQUIRED)
endif(BUILD_MISSING_DEPENDENCIES)

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
if(BUILD_TESTING)
	enable_testing()

	#Code style validation.
	find_python_module(pylint REQUIRED)
	file(GLOB_RECURSE python_files *.py)
	add_test(NAME CodeStyle COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylintrc ${python_files})
	set_tests_properties(CodeStyle PROPERTIES ENVIRONMENT PYTHONPATH=${CMAKE_SOURCE_DIR})
endif(BUILD_TESTING)

#Documentation
if(BUILD_DOCUMENTATION)
	find_package(Sphinx REQUIRED)
	set(DOCUMENTATION_OUTPUT_DIR "${CMAKE_CURRENT_BINARY_DIR}/documentation")
	configure_file("${CMAKE_SOURCE_DIR}/sphinx_configuration.py.in" "${CMAKE_BINARY_DIR}/sphinx_configuration.py" @ONLY)
	add_custom_target(documentation ALL ${SPHINX_EXECUTABLE} -n "${CMAKE_SOURCE_DIR}" "${DOCUMENTATION_OUTPUT_DIR}" COMMENT "Generate technical documentation of the application.")
endif(BUILD_DOCUMENTATION)
