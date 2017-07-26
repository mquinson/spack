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
from spack import *
import os
import sys

def get_submodules():
    git = which('git')
    git('submodule', 'update', '--init', '--recursive')

class Chameleon(Package):
    """Dense Linear Algebra for Scalable Multi-core Architectures and GPGPUs"""
    homepage = "https://gitlab.inria.fr/solverstack/chameleon"

    version('master', git='https://gitlab.inria.fr/solverstack/chameleon.git', submodules=True)

    variant('shared', default=True, description='Build chameleon as a shared library')
    variant('mpi', default=True, description='Enable MPI')
    variant('cuda', default=False, description='Enable CUDA')
    variant('fxt', default=True, description='Enable FxT tracing support through StarPU')
    variant('simgrid', default=False, description='Enable simulation mode through StarPU+SimGrid')
    variant('starpu', default=True, description='Use StarPU runtime')
    variant('quark', default=False, description='Use Quark runtime instead of StarPU')
    variant('examples', default=True, description='Enable compilation and installation of example executables')

    depends_on("cmake")
    depends_on("blas", when='~simgrid')
    depends_on("lapack", when='~simgrid')
    depends_on("starpu", when='+starpu')
    depends_on("starpu~mpi", when='+starpu~mpi')
    depends_on("starpu+cuda", when='+starpu+cuda~simgrid')
    depends_on("starpu+fxt", when='+starpu+fxt')
    depends_on("starpu+simgrid", when='+starpu+simgrid')
    depends_on("starpu+mpi~shared+simgrid", when='+starpu+simgrid+mpi')
    depends_on("quark", when='+quark')
    depends_on("mpi", when='+mpi~simgrid')
    depends_on("cuda", when='+cuda~simgrid')
    depends_on("magma@1.6.2", when='+magma+cuda~simgrid')
    depends_on("fxt", when='+fxt+starpu')

    def install(self, spec, prefix):

        if spec.satisfies('@master'):
            get_submodules()

        with working_dir('spack-build', create=True):

            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            if spec.satisfies('+shared'):
                # Enable build shared libs.
                cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])

            if spec.satisfies('+examples'):
                # Enable Examples here.
                cmake_args.extend(["-DCHAMELEON_ENABLE_EXAMPLE=ON"])
                cmake_args.extend(["-DCHAMELEON_ENABLE_TESTING=ON"])
                cmake_args.extend(["-DCHAMELEON_ENABLE_TIMING=ON"])
            else:
                # Enable Examples here.
                cmake_args.extend(["-DCHAMELEON_ENABLE_EXAMPLE=OFF"])
                cmake_args.extend(["-DCHAMELEON_ENABLE_TESTING=OFF"])
                cmake_args.extend(["-DCHAMELEON_ENABLE_TIMING=OFF"])
            if spec.satisfies('+debug'):
                # Enable Debug here.
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
            if spec.satisfies('+mpi'):
                # Enable MPI here.
                cmake_args.extend(["-DCHAMELEON_USE_MPI=ON"])
            if spec.satisfies('+cuda'):
                # Enable CUDA here.
                cmake_args.extend(["-DCHAMELEON_USE_CUDA=ON"])
            else:
                cmake_args.extend(["-DCHAMELEON_USE_CUDA=OFF"])
            if spec.satisfies('+fxt'):
                # Enable FxT here.
                cmake_args.extend(["-DCHAMELEON_ENABLE_TRACING=ON"])
            if spec.satisfies('+simgrid'):
                # Enable SimGrid here.
                cmake_args.extend(["-DCHAMELEON_SIMULATION=ON"])
            if spec.satisfies('+quark') and spec.satisfies('+starpu'):
                raise RuntimeError('variant +quark and +starpu are mutually exclusive, please choose one.')
            if spec.satisfies('~quark') and spec.satisfies('~starpu'):
                raise RuntimeError('Chameleon requires a runtime system to be enabled, either +quark or +starpu, please choose one.')
            if spec.satisfies('+quark'):
                # Enable Quark here.
                cmake_args.extend(["-DCHAMELEON_SCHED_QUARK=ON"])
            else:
                cmake_args.extend(["-DCHAMELEON_SCHED_QUARK=OFF"])
            if spec.satisfies('+starpu'):
                # Enable StarPU here.
                starpu = self.spec['starpu']
                cmake_args.extend(["-DCHAMELEON_SCHED_STARPU=ON"])
            else:
                cmake_args.extend(["-DCHAMELEON_SCHED_STARPU=OFF"])

            if spec.satisfies('~simgrid'):
                blas = self.spec['blas']
                lapack = self.spec['lapack']

                blas_libs = spec['blas'].libs.ld_flags
                blas_libs = blas_libs.replace(' ', ';')
                cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])
                try:
                    blas_flags = spec['blas'].headers.cpp_flags
                except AttributeError:
                    blas_flags = ''

                cmake_args.extend(['-DBLAS_COMPILER_FLAGS=%s' % blas_flags])
                lapack_libs = spec['lapack'].libs.ld_flags
                lapack_libs = lapack_libs.replace(' ', ';')
                cmake_args.extend(['-DLAPACK_LIBRARIES=%s' % lapack_libs])

                if spec.satisfies('%gcc'):
                    cmake_args.extend(['-DCMAKE_EXE_LINKER_FLAGS=-lgfortran'])

            cmake(*cmake_args)
            make()
            make("install")
