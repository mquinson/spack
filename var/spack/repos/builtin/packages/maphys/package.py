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
#     spack install maphys
#
# You can edit this file again by typing:
#
#     spack edit maphys
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *

class Maphys(Package):
    """a Massively Parallel Hybrid Solver."""

    homepage = "https://gitlab.inria.fr/solverstack/maphys"
    url      = "https://gitlab.inria.fr/solverstack/maphys"
    gitroot  = "https://gitlab.inria.fr/solverstack/maphys.git"

    version('master' , git=gitroot, branch='master', submodules=True)
    version('develop', git=gitroot, branch='develop', submodules=True)

    #version('paddle', git=gitroot, branch='feature/paddle', submodules=True)

    version('0.9.5', '53289def2993d9882e724e3a659cd200',
            url='http://morse.gforge.inria.fr/maphys/maphys-0.9.5.1.tar.gz')
    version('0.9.5.1', '53289def2993d9882e724e3a659cd200',
            url='http://morse.gforge.inria.fr/maphys/maphys-0.9.5.1.tar.gz' , preferred=True)
    version('0.9.5.0', '8bc00e6597ef5b780243a794c6f71700',
            url='http://morse.gforge.inria.fr/maphys/maphys-0.9.5.0.tar.gz')

    variant('debug', default=False, description='Enable debug symbols')
    variant('shared', default=True, description='Build MaPHyS as a shared library')
    variant('blasmt', default=False, description='Enable to use MPI+Threads version of MaPHyS, a multithreaded Blas/Lapack library is required (MKL, ESSL, OpenBLAS)')
    variant('mumps', default=True, description='Enable MUMPS direct solver')
    variant('examples', default=True, description='Enable compilation and installation of example executables')

    #variant('pastix', default=True, description='Enable PASTIX direct solver')
    #variant('fabulous', default=False, description='Enable FABuLOuS iterative solver')
    #variant('paddle', default=False, description='Enable Paddle domain decomposer')


    depends_on("cmake")
    depends_on("mpi")
    depends_on("hwloc")
    depends_on("scotch+mpi+esmumps", when='+mumps')
    depends_on("scotch+mpi~esmumps", when='~mumps')
    depends_on("blas")
    depends_on("lapack")
    # TODO: pastix
    #depends_on("pastix+mpi~metis", when='+pastix')
    #depends_on("pastix+mpi+blasmt~metis", when='+pastix+blasmt')
    depends_on("mumps+mpi", when='+mumps')
    depends_on("mumps+mpi+blasmt", when='+mumps+blasmt')
    # TODO: fabulous
    #depends_on('fabulous@ib', when='+fabulous')
    # TODO: paddle
    #depends_on('paddle', when='+paddle')

    def install(self, spec, prefix):

        with working_dir('spack-build', create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            # Static / Shared library
            if spec.satisfies('+shared'):
                cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])

            # Debug / Release
            if spec.satisfies('+debug'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
            else:
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])

            # Compile exemples and tests
            if spec.satisfies('+examples'):
                cmake_args.extend(["-DMAPHYS_BUILD_EXAMPLES=ON"])
                cmake_args.extend(["-DMAPHYS_BUILD_TESTS=ON"])
            else:
                cmake_args.extend(["-DMAPHYS_BUILD_EXAMPLES=OFF"])
                cmake_args.extend(["-DMAPHYS_BUILD_TESTS=OFF"])

            # With or without Mumps
            if spec.satisfies('~mumps'):
                cmake_args.extend(["-DMAPHYS_SDS_MUMPS=OFF"])

            # With or without Pastix
            #if spec.satisfies('~pastix'):
            #    cmake_args.extend(["-DMAPHYS_SDS_PASTIX=OFF"])
            cmake_args.extend(["-DMAPHYS_SDS_PASTIX=OFF"])

            # Blas
            blas_libs = spec['blas'].libs.ld_flags
            if spec.satisfies('+blasmt'):
                cmake_args.extend(["-DMAPHYS_BLASMT=ON"])
                if '^mkl' in spec or '^essl' in spec or '^openblas+mt' in spec:
                    blas_libs = spec['blas'].mkl_libs
                else:
                    raise RuntimeError('Only ^openblas+mt, ^mkl and ^essl provide multithreaded blas.')
            cmake_args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])
            try:
                blas_flags = spec['blas'].libs.ld_flags
            except AttributeError:
                blas_flags = ''
            cmake_args.extend(['-DBLAS_COMPILER_FLAGS=%s' % blas_flags])

            # Lapack
            lapack_libs = spec['lapack'].libs.ld_flags
            if spec.satisfies('+blasmt'):
                if '^mkl' in spec:
                    lapack_libs = spec['lapack'].libs.ld_flags # MT?
                else:
                    raise RuntimeError('Only ^mkl provide multithreaded lapack.')
            cmake_args.extend(["-DLAPACK_LIBRARIES=%s" % lapack_libs])

            # Scalapack
            if spec.satisfies('+mumps^mpi'):
                scalapack_libs = '%s' % (spec['scalapack'].libs.ld_flags)
                cmake_args.extend(["-DSCALAPACK_LIBRARIES=%s" % scalapack_libs])

            # Fabulous
            #if spec.satisfies('+fabulous'):
            #    cmake_args.extend(["-DCMAKE_EXE_LINKER_FLAGS=-lstdc++"])
            #    cmake_args.extend(["-DMAPHYS_ITE_IBBGMRESDR=ON"])
            #    fabulous_libs = spec['fabulous'].cc_link
            #    cmake_args.extend(["-DIBBGMRESDR_LIBRARIES=%s" % fabulous_libs])
            #    fabulous_inc = spec['fabulous'].prefix.include
            #    cmake_args.extend(["-DIBBGMRESDR_INCLUDE_DIRS=%s" % fabulous_inc])
            #
            # Paddle
            #if spec.satisfies('+paddle'):
            #    cmake_args.extend(["-DMAPHYS_ORDERING_PADDLE=ON"])
            #    paddle_lib = spec['paddle'].cc_link
            #    paddle_inc = spec['paddle'].cc_flags
            #    cmake_args.extend(["-DPADDLE_INCLUDE_DIRS=%s" % paddle_inc])
            #    cmake_args.extend(["-DPADDLE_LIBRARIES=%s" % paddle_lib])

            cmake(*cmake_args)

            #install_tree('lib', prefix.lib)
            #install_tree('include', prefix.include)

            make()
            make("install")
