#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

function(get_mime_types plugin_dir)
	#Turn the plug-in directory to something Python can import.
	file(RELATIVE_PATH plugin_dir_relative ${CMAKE_SOURCE_DIR} ${plugin_dir})
	get_filename_component(plugin_name ${plugin_dir_relative} NAME) #Get the name as import alias.
	get_filename_component(parent_dir ${plugin_dir} DIRECTORY) #Where to import it from.
	#Execute the init file and get Python to print the list of MIME types.
	execute_process( #Imports the project in the same way as in luna.plugins._load_candidates.
		COMMAND "${PYTHON_EXECUTABLE}" "-c" "import imp
file, path, description = imp.find_module('${plugin_name}', ['${parent_dir}'])
module = imp.load_module('${plugin_name}', file, path, description)
metadata = module.metadata()['data']
result = []
for extension in metadata['extensions']:
	result.append(metadata['mimetype'] + '|' + metadata['name'] + '|' + extension)
print(';'.join(result))"
		WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
		RESULT_VARIABLE python_status
		OUTPUT_VARIABLE found_mime_types
		ERROR_QUIET
		OUTPUT_STRIP_TRAILING_WHITESPACE
	)
	if(NOT python_status) #Success.
		foreach(mime ${found_mime_types})
			string(REPLACE "|" ";" mime_data ${mime})
			list(GET mime_data 0 mime_type)
			list(GET mime_data 1 mime_name)
			list(GET mime_data 2 mime_extension)
			list(APPEND MIME_TYPES ${mime_type})
			list(APPEND MIME_NAMES ${mime_name})
			list(APPEND MIME_EXTENSIONS ${mime_extension})
		endforeach()
		set(MIME_TYPES ${MIME_TYPES} PARENT_SCOPE)
		set(MIME_NAMES ${MIME_NAMES} PARENT_SCOPE)
		set(MIME_EXTENSIONS ${MIME_EXTENSIONS} PARENT_SCOPE)
	endif()
endfunction()