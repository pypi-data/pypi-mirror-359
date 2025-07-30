# This file is included during
#
#    find_package( falfilfa [COMPONENTS (double|single)] [QUIET] [REQUIRED] )
#
# Supported COMPONENTS: double single 
#
# If available following targets will be exported:
# - fa_dp  Double precision falfilfa library
# - fa_sp  Single precision falfilfa library


##################################################################
## Export project variables

set( falfilfa_VERSION_STR             1.0.7 )
set( falfilfa_HAVE_SINGLE_PRECISION   0 )
set( falfilfa_HAVE_DOUBLE_PRECISION   True )
set( falfilfa_REQUIRES_PRIVATE_DEPENDENCIES  )

if( NOT ${CMAKE_FIND_PACKAGE_NAME}_FIND_QUIETLY )
  message( STATUS "Found falfilfa version ${falfilfa_VERSION_STR}" )
endif()

##################################################################
## Export project dependencies

include( CMakeFindDependencyMacro )
if( falfilfa_REQUIRES_PRIVATE_DEPENDENCIES OR CMAKE_Fortran_COMPILER_LOADED )
    if( NOT CMAKE_Fortran_COMPILER_LOADED )
        enable_language( Fortran )
    endif()
    find_dependency( fiat HINTS ${CMAKE_CURRENT_LIST_DIR}/../fiat PATHS /work/tmp/install/lib64/cmake/fiat  )
    find_dependency( eccodes HINTS ${CMAKE_CURRENT_LIST_DIR}/../eccodes PATHS   )
endif()


##################################################################
## Handle components

set( ${CMAKE_FIND_PACKAGE_NAME}_single_FOUND ${falfilfa_HAVE_SINGLE_PRECISION} )
set( ${CMAKE_FIND_PACKAGE_NAME}_double_FOUND ${falfilfa_HAVE_DOUBLE_PRECISION} )

foreach( _component ${${CMAKE_FIND_PACKAGE_NAME}_FIND_COMPONENTS} )
  if( NOT ${CMAKE_FIND_PACKAGE_NAME}_${_component}_FOUND AND ${CMAKE_FIND_PACKAGE_NAME}_FIND_REQUIRED )
    message( SEND_ERROR "falfilfa was not build with support for COMPONENT ${_component}" )
  endif()
endforeach()
