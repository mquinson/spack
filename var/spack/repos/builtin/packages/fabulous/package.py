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


class Fabulous(Package):
    """FABuLOuS (Fast Accurate Block Linear krylOv Solver)
    Library implementing Block-GMres with Inexact Breakdown and Deflated Restarting"""

    homepage = "https://gforge.inria.fr/projects/ib-bgmres-dr/"
    gitroot="https://gitlab.inria.fr/solverstack/fabulous.git"

    version("develop", git=gitroot,  branch="develop", preferred=True, submodules=True)
    version("ib", git=gitroot, branch="ib", submodules=True)
    version("0.3", git=gitroot, branch="release/0.3", submodules=True)

    variant("shared", default=True, description="Build as shared library")
    variant("debug", default=False, description="Enable debug symbols")
    #variant("chameleon", default=False, description="build extra chameleon backend")
    variant("examples", default=False, description="build examples and tests")
    variant("blasmt", default=False, description="use multi-threaded blas and lapack kernels")

    depends_on("cmake")
    depends_on("blas")
    depends_on("lapack")
    #depends_on("chameleon@master", when="+chameleon")

    def install(self, spec, prefix):

        with working_dir("spack-build", create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            # old versions of cmake use gcc instead of g++
            # to link a C application with a C++ library:
            cmake_args.extend(["-DCMAKE_EXE_LINKER_FLAGS=-lstdc++"])

            cmake_args.extend(['-DCBLAS_DIR=%s' % spec['blas'].prefix ])
            cmake_args.extend(['-DLAPACKE_DIR=%s' % spec['lapack'].prefix])
            cmake_args.extend(['-DBLAS_DIR=%s' % spec['blas'].prefix ])
            cmake_args.extend(['-DLAPACK_DIR=%s' % spec['lapack'].prefix])

            if spec.satisfies("+blasmt"):
                # Enable multithreaded blas
                cmake_args.extend(["-DFABULOUS_BLASMT=ON"])
            else:
                cmake_args.extend(["-DFABULOUS_BLASMT=OFF"])

            if spec.satisfies("+shared"):
                # Enable build shared libs
                cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])
            else:
                cmake_args.extend(["-DBUILD_SHARED_LIBS=OFF"])

            # This must stay like this until tpmqrt lapacke iface
            # workspace bug is fixed in lapacke releases
            # and COMMONLY DEPLOYED (Fixed in Lapack 3.7.1 (25 June 2017))
            cmake_args.extend(["-DFABULOUS_LAPACKE_NANCHECK=OFF"])

            if spec.satisfies("+debug"):
                cmake_args.extend(["-DFABULOUS_DEBUG_MODE=ON"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
            else:
                cmake_args.extend(["-DFABULOUS_DEBUG_MODE=OFF"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])

            #if spec.satisfies("+chameleon"):
            #    cham_prefix = spec["chameleon"].prefix
            #    cmake_args.extend(["-DCHAMELEON_DIR="+cham_prefix])
            #    cmake_args.extend(["-DFABULOUS_USE_CHAMELEON=ON"])
            #else:
            #    cmake_args.extend(["-DFABULOUS_USE_CHAMELEON=OFF"])
            cmake_args.extend(["-DFABULOUS_USE_CHAMELEON=OFF"])

            if spec.satisfies("+examples"):
                cmake_args.extend(["-DFABULOUS_BUILD_EXAMPLES=ON"])
                cmake_args.extend(["-DFABULOUS_BUILD_TESTS=ON"])
            else:
                cmake_args.extend(["-DFABULOUS_BUILD_EXAMPLES=OFF"])
                cmake_args.extend(["-DFABULOUS_BUILD_TESTS=OFF"])

            cmake(*cmake_args)
            make()
            make("install")
