#This software is distributed under the Creative Commons license (CC0) version 1.0. A copy of this license should have been distributed with this software.
#The license can also be read online: <https://creativecommons.org/publicdomain/zero/1.0/>. If this online license differs from the license provided with this software, the license provided with this software should be applied.

find_program(SPHINX_EXECUTABLE NAMES sphinx-build HINTS $ENV{SPHINX_DIR} PATH_SUFFIXES bin DOC "Sphinx documentation generator.")
include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Sphinx DEFAULT_MSG SPHINX_EXECUTABLE)

find_program(SPHINX_APIDOC_EXECUTABLE NAMES sphinx-apidoc HINTS $ENV{SPHINX_DIR} PATH_SUFFIXES bin DOC "Sphinx generator for reStructuredText API files of Python source code.")
find_package_handle_standard_args(Sphinx-apidoc DEFAULT_MSG SPHINX_APIDOC_EXECUTABLE)

mark_as_advanced(SPHINX_EXECUTABLE)
mark_as_advanced(SPHINX_APIDOC_EXECUTABLE)