cmake_minimum_required(VERSION 2.6)
project(Luna)

#Dependencies.
find_package(PythonInterp 3.4.0 REQUIRED)

#Validation target.
set(VALIDATE_PYLINT_EXECUTABLE pylint CACHE FILEPATH "Path to the PyLint executable.")
set(validateCommands) #List of commands to validate the code.
set(validatePythonFiles) #List of Python files to validate with PyLint.
file(GLOB_RECURSE pythonSources *.py)
foreach(pythonFile ${pythonSources})
	get_filename_component(pythonFileAbsolute ${pythonFile} ABSOLUTE)
	list(APPEND validatePythonFiles ${pythonFileAbsolute})
endforeach(pythonFile)
list(APPEND validateCommands COMMAND ${VALIDATE_PYLINT_EXECUTABLE} ${validatePythonFiles} --rcfile=${CMAKE_SOURCE_DIR}/pylintrc)
add_custom_target(validate ${validateCommands} VERBATIM)