#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

option(BUILD_SPHINX "Build the Sphinx dependency from source." FALSE)

if(BUILD_SPHINX)
	if(NOT SPHINX_FOUND)
		message(STATUS "Building Sphinx from source.")
		include(ExternalProject)
		find_package(PythonInterp 3.4.0 REQUIRED)
		ExternalProject_Add(Sphinx
			URL https://pypi.python.org/packages/8b/78/eeea2b837f911cdc301f5f05163f9729a2381cadd03ccf35b25afe816c90/Sphinx-1.4.5.tar.gz#md5=5c2cd2dac45dfa6123d067e32a89e89a
			URL_HASH SHA512=E11CA5E02C44A2112CA31E1CFF4DB8A89AC0D58E410AEF43EAD48C74520DACAE61BA8AA5B91C5F6EF920851E35A2FF1470E74FD038CB50AC9BB6F689C495CEE7
			CONFIGURE_COMMAND ""
			BUILD_COMMAND ${PYTHON_EXECUTABLE} setup.py build
			INSTALL_COMMAND ${PYTHON_EXECUTABLE} setup.py install
			BUILD_IN_SOURCE 1
		)
		set(SPHINX_EXECUTABLE sphinx-build)
		set(SPHINX_APIDOC_EXECUTABLE sphinx-apidoc)
		set(SPHINX_FOUND TRUE)
	endif(NOT SPHINX_FOUND)
else(BUILD_SPHINX) #Just find it on the system.
	include(FindPackageHandleStandardArgs)
	find_program(SPHINX_EXECUTABLE NAMES sphinx-build HINTS $ENV{SPHINX_DIR} PATH_SUFFIXES bin DOC "Sphinx documentation generator.")
	find_package_handle_standard_args(Sphinx DEFAULT_MSG SPHINX_EXECUTABLE)
	find_program(SPHINX_APIDOC_EXECUTABLE NAMES sphinx-apidoc HINTS $ENV{SPHINX_DIR} PATH_SUFFIXES bin DOC "Sphinx generator for reStructuredText API files of Python source code.")
	find_package_handle_standard_args(Sphinx-apidoc DEFAULT_MSG SPHINX_APIDOC_EXECUTABLE)
endif(BUILD_SPHINX)

mark_as_advanced(SPHINX_EXECUTABLE)
mark_as_advanced(SPHINX_APIDOC_EXECUTABLE)