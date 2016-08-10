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
	find_package_handle_standard_args(PYTHON_${module} DEFAULT_MSG PYTHON_${module_uppercase})
endfunction(find_python_module)