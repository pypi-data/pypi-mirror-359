#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "fa_dp" for configuration "Debug"
set_property(TARGET fa_dp APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(fa_dp PROPERTIES
  IMPORTED_LOCATION_DEBUG "${_IMPORT_PREFIX}/lib64/libfa_dp.so"
  IMPORTED_SONAME_DEBUG "libfa_dp.so"
  )

list(APPEND _cmake_import_check_targets fa_dp )
list(APPEND _cmake_import_check_files_for_fa_dp "${_IMPORT_PREFIX}/lib64/libfa_dp.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
