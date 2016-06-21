cmake_minimum_required(VERSION 2.6)
project(Luna)

#Dependencies.
find_package(PythonInterp 3.4.0 REQUIRED)

#Tests
option(BUILD_TESTING "Build a target for automatically testing the code." TRUE)
if(BUILD_TESTING)
	enable_testing()

	#Code style validation test.
	file(GLOB_RECURSE pythonFiles *.py)
	add_test(NAME CodeStyleValidation COMMAND ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylintrc ${pythonFiles})
endif(BUILD_TESTING)