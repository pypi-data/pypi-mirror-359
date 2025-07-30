#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) Météo France (2014-)
# This software is governed by the CeCILL-C license under French law.
# http://www.cecill.info
"""
falfilfa4py:

Contains the interface routines to IO libraries for formats:
- LFI
- FA (overlay of LFI)
- LFA (DDH format)
"""
import os
import resource
import ctypesForFortran
import logging

logger = logging.getLogger(__name__)

__version__ = "1.0.7"
# warning ensure consistency with VERSION file

# Shared objects library
########################
so_basename = "libfa_dp.so"  # local name of library in the directory
LD_LIBRARY_PATH = [p for p in os.environ.get('LD_LIBRARY_PATH', '').split(':') if p != '']
lpath = LD_LIBRARY_PATH + [
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'),
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib64'),
        ]
for d in lpath:
    shared_objects_library = os.path.join(d, so_basename)
    if os.path.exists(shared_objects_library):
        break
    else:
        shared_objects_library = None
if shared_objects_library is None:
    msg = ' '.join(["'{}' was not found in any of potential locations: {}.",
                    "You can specify a different location using env var LD_LIBRARY_PATH"])
    msg = msg.format(so_basename, str(lpath))
    raise FileNotFoundError(msg)

ctypesFF, handle = ctypesForFortran.ctypesForFortranFactory(shared_objects_library)

def get_dynamic_eccodes_lib_path_from_FA():
    """DEPRECATED: Get paths to the eccodes linked for FA purpose in the shared objects library."""
    logger.info("DEPRECATED: not reliable with recent versions of eccodes.")
    for l, libpath in ctypesForFortran.get_dynamic_libs(shared_objects_library).items():
        if l.startswith('libeccodes'):
            return libpath

# Initialization
################

def init_env(omp_num_threads=None,
             no_mpi=False,
             lfi_C=False,
             mute_FA4py=False,
             unlimited_stack=False,
             fa_limits={}):
    """
    Set adequate environment for the inner libraries.

    :param int omp_num_threads: sets OMP_NUM_THREADS
    :param bool no_mpi: environment variable DR_HOOK_NOT_MPI set to 1
    :param bool lfi_C: if True, LFI_HNDL_SPEC set to ':1', to use the C version of LFI
    :param bool mute_FA4py: mute messages from FAIPAR in FA4py library
    :param unlimited_stack: equivalent to 'ulimit -s unlimited'
    :param fa_limits: FA limits
    """
    # because arpifs library is compiled with MPI & openMP
    if omp_num_threads is not None:
        os.environ['OMP_NUM_THREADS'] = str(omp_num_threads)
    if no_mpi:
        os.environ['DR_HOOK_NOT_MPI'] = '1'
    # use the C library for LFI
    if lfi_C:
        os.environ['LFI_HNDL_SPEC'] = ':1'
    # option for FA
    if mute_FA4py:
        os.environ['FA4PY_MUTE'] = '1'
    # ulimit -s unlimited
    if unlimited_stack:
        resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY,resource.RLIM_INFINITY))
    # warning if ECCODES PATHs variables are defined
    for v in ('ECCODES_SAMPLES_PATH','ECCODES_DEFINITION_PATH'):
        if os.environ.get(v, None):
            logger.warning(" ".join([v, "env var is defined:",
                                     "may result in unexpected issues if not consistent with linked eccodes library"]))
    if fa_limits != {}:
        from . import FA
        FA.set_fa_limits(**fa_limits)


# sub-modules
#############
from . import FA
from . import LFI
from . import LFA
