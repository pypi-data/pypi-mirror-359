# Config file for the falfilfa package
# Defines the following variables:
#
#  falfilfa_FEATURES       - list of enabled features
#  falfilfa_VERSION        - version of the package
#  falfilfa_GIT_SHA1       - Git revision of the package
#  falfilfa_GIT_SHA1_SHORT - short Git revision of the package
#


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was project-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################

### computed paths
set_and_check(falfilfa_CMAKE_DIR "${PACKAGE_PREFIX_DIR}/lib64/cmake/falfilfa")
set_and_check(falfilfa_BASE_DIR "${PACKAGE_PREFIX_DIR}/.")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FALFILFA_CMAKE_DIR ${falfilfa_CMAKE_DIR})
  set(FALFILFA_BASE_DIR ${falfilfa_BASE_DIR})
endif()

### export version info
set(falfilfa_VERSION           "1.0.7")
set(falfilfa_GIT_SHA1          "e4403f8a69f09f2c3d0afd1448c1c90c088907fd")
set(falfilfa_GIT_SHA1_SHORT    "e4403f8")

if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FALFILFA_VERSION           "1.0.7" )
  set(FALFILFA_GIT_SHA1          "e4403f8a69f09f2c3d0afd1448c1c90c088907fd" )
  set(FALFILFA_GIT_SHA1_SHORT    "e4403f8" )
endif()

### has this configuration been exported from a build tree?
set(falfilfa_IS_BUILD_DIR_EXPORT OFF)
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FALFILFA_IS_BUILD_DIR_EXPORT ${falfilfa_IS_BUILD_DIR_EXPORT})
endif()

### include the <project>-import.cmake file if there is one
if(EXISTS ${falfilfa_CMAKE_DIR}/falfilfa-import.cmake)
  set(falfilfa_IMPORT_FILE "${falfilfa_CMAKE_DIR}/falfilfa-import.cmake")
  include(${falfilfa_IMPORT_FILE})
endif()

### insert definitions for IMPORTED targets
if(NOT falfilfa_BINARY_DIR)
  find_file(falfilfa_TARGETS_FILE
    NAMES falfilfa-targets.cmake
    HINTS ${falfilfa_CMAKE_DIR}
    NO_DEFAULT_PATH)
  if(falfilfa_TARGETS_FILE)
    include(${falfilfa_TARGETS_FILE})
  endif()
endif()

### include the <project>-post-import.cmake file if there is one
if(EXISTS ${falfilfa_CMAKE_DIR}/falfilfa-post-import.cmake)
  set(falfilfa_POST_IMPORT_FILE "${falfilfa_CMAKE_DIR}/falfilfa-post-import.cmake")
  include(${falfilfa_POST_IMPORT_FILE})
endif()

### handle third-party dependencies
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FALFILFA_LIBRARIES         "")
  set(FALFILFA_TPLS              "" )

  include(${CMAKE_CURRENT_LIST_FILE}.tpls OPTIONAL)
endif()

### publish this file as imported
if( DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT )
  set(falfilfa_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(falfilfa_IMPORT_FILE)
  set(FALFILFA_IMPORT_FILE ${CMAKE_CURRENT_LIST_FILE})
  mark_as_advanced(FALFILFA_IMPORT_FILE)
endif()

### export features and check requirements
set(falfilfa_FEATURES "PKGCONFIG;DOUBLE_PRECISION;DOUBLE_PRECISION")
if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
  set(FALFILFA_FEATURES ${falfilfa_FEATURES})
endif()
foreach(_f ${falfilfa_FEATURES})
  set(falfilfa_${_f}_FOUND 1)
  set(falfilfa_HAVE_${_f} 1)
  if(DEFINED ECBUILD_2_COMPAT AND ECBUILD_2_COMPAT)
    set(FALFILFA_HAVE_${_f} 1)
  endif()
endforeach()
check_required_components(falfilfa)
