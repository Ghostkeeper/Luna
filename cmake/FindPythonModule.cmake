#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

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
			set(PYTHON_${module_uppercase}_FOUND TRUE PARENT_SCOPE)
		else(NOT _${module}_status)
			set(PYTHON_${module_uppercase}_FOUND FALSE PARENT_SCOPE)
		endif(NOT _${module}_status)
	else(NOT PYTHON_${module_uppercase})
		set(PYTHON_${module_uppercase}_FOUND TRUE PARENT_SCOPE)
	endif(NOT PYTHON_${module_uppercase})
	include(FindPackageHandleStandardArgs)
	find_package_handle_standard_args(PYTHON_${module} DEFAULT_MSG PYTHON_${module_uppercase})
endfunction(find_python_module)