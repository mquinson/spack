##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install fabulous
#
# You can edit this file again by typing:
#
#     spack edit fabulous
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *


class Fabulous(CMakePackage):
    """FABuLOuS (Fast Accurate Block Linear krylOv Solver)
    Library implementing Block-GMres with Inexact Breakdown and Deflated Restarting"""

    homepage = "https://gforge.inria.fr/projects/ib-bgmres-dr/"
    gitroot="https://gitlab.inria.fr/solverstack/fabulous.git"

    version("develop", git=gitroot,  branch="develop", preferred=True, submodules=True)
    version("ib", git=gitroot, branch="ib", submodules=True)
    version("0.3", git=gitroot, branch="release/0.3", submodules=True)

    variant("shared", default=True, description="Build as shared library")
    variant("debug", default=False, description="Enable debug symbols")
    variant("examples", default=False, description="build examples and tests")
    variant("blasmt", default=False, description="use multi-threaded blas and lapack kernels")

    depends_on("blas")
    depends_on("lapack")

    def cmake_args(self):
        spec = self.spec

        args = std_cmake_args
        args.remove('-DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo')

        args.extend([

            # old versions of cmake use gcc instead of g++
            # to link a C application with a C++ library:
            "-DCMAKE_EXE_LINKER_FLAGS=-lstdc++",

            # This must stay like this until tpmqrt lapacke iface
            # workspace bug is fixed in lapacke releases
            # and COMMONLY DEPLOYED (Fixed in Lapack 3.7.1 (25 June 2017))
            "-DFABULOUS_LAPACKE_NANCHECK=OFF",
            "-DFABULOUS_USE_CHAMELEON=OFF",

            "-DCBLAS_DIR=%s"   % spec['blas'].prefix,
            "-DLAPACKE_DIR=%s" % spec['lapack'].prefix,
            "-DBLAS_DIR=%s"    % spec['blas'].prefix,
            "-DLAPACK_DIR=%s"  % spec['lapack'].prefix,
            "-DCMAKE_BUILD_TYPE=%s"    % ('Debug'  if '+debug'    in spec else 'Release'),
            "-DFABULOUS_DEBUG_MODE=%s" % ('ON'     if '+debug'    in spec else 'OFF'),
            "-DBUILD_SHARED_LIBS=%s"   % ('ON'     if '+shared'   in spec else 'OFF'),
            "-DFABULOUS_BLASMT=%s"     % ('ON'     if '+blasmt'   in spec else 'OFF'),
            "-DFABULOUS_BUILD_EXAMPLES=%s" % ('ON' if '+examples' in spec else 'OFF'),
            "-DFABULOUS_BUILD_TESTS=%s"    % ('ON' if '+examples' in spec else 'OFF'),
        ])

        return args
