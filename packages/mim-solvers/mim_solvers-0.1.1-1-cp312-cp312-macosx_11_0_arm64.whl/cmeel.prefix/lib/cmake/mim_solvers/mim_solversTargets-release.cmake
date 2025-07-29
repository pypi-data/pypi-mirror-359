#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "mim_solvers::mim_solvers" for configuration "Release"
set_property(TARGET mim_solvers::mim_solvers APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(mim_solvers::mim_solvers PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libmim_solvers.0.1.1.dylib"
  IMPORTED_SONAME_RELEASE "@rpath/libmim_solvers.0.1.1.dylib"
  )

list(APPEND _cmake_import_check_targets mim_solvers::mim_solvers )
list(APPEND _cmake_import_check_files_for_mim_solvers::mim_solvers "${_IMPORT_PREFIX}/lib/libmim_solvers.0.1.1.dylib" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
