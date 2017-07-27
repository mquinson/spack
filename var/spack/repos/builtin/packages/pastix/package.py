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
#     spack install pastix
#
# You can edit this file again by typing:
#
#     spack edit pastix
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
from spack import *
from shutil import copyfile
import os

class Pastix(CMakePackage):
    """a high performance parallel solver for very large sparse linear systems based on direct methods"""

    homepage = "http://pastix.gforge.inria.fr/files/README-txt.html"
    url      = "https://gforge.inria.fr/frs/download.php/file/36212/pastix_5.2.3.tar.bz2"

    version('solverstack', git="git@gitlab.inria.fr:solverstack/pastix.git", submodules=True)

    version('5.2.3', '31a1c3ea708ff2dc73280e4b85a82ca8',
            url='https://gforge.inria.fr/frs/download.php/file/36212/pastix_5.2.3.tar.bz2')
    version('develop', git='https://scm.gforge.inria.fr/anonscm/git/ricar/ricar.git', branch='develop')

    # Variants

    variant('mpi', default=True, description='Enable MPI')
    variant('smp', default=True, description='Enable Thread')
    variant('blasmt', default=False, description='Enable to use multithreaded Blas library (MKL, ESSL, OpenBLAS)')
    variant('cuda', default=False, description='Enable CUDA kernels. Caution: only available if StarPU variant is enabled')
    variant('metis', default=True, description='Enable Metis')
    variant('scotch', default=True, description='Enable Scotch')
    variant('starpu', default=False, description='Enable StarPU')
    variant('shared', default=True, description='Build Pastix as a shared library')
    variant('examples', default=True, description='Enable compilation and installation of example executables')
    variant('debug', default=False, description='Enable debug symbols')
    variant('idx64', default=False, description='To use 64 bits integers')
    variant('dynsched', default=False, description='Enable dynamic thread scheduling support')
    variant('memory', default=True, description='Enable memory usage statistics')
    variant('murgeup', default=False, description='Pull git murge source code (internet connection required), useful for the develop branch')
    # TODO
    #variant('pypastix', default=False, description='Create a python 2 wrapper for pastix called pypastix')
    #variant('pypastix3', default=False, description='Create a python 3 wrapper for pastix called pypastix')

    # Dependencies

    depends_on("hwloc")
    depends_on("hwloc+cuda", when='+cuda')
    depends_on("mpi", when='+mpi')
    depends_on("blas")
    depends_on("scotch", when='+scotch')
    depends_on("scotch~mpi", when='+scotch~mpi')
    depends_on("scotch+idx64", when='+scotch+idx64')
    depends_on("metis@5.1:", when='+metis')
    depends_on("metis@5.1:+idx64", when='+metis+idx64')
    depends_on("starpu", when='+starpu')
    depends_on("starpu~mpi", when='+starpu~mpi')
    depends_on("starpu+cuda", when='+starpu+cuda')

    @property
    def root_cmakelists_dir(self):
        if '@solverstack' not in self.spec:
            return os.path.join(self.stage.source_path, 'src')
        return self.stage.source_path

    def cmake_args(self):
        spec = self.spec

        if '@solverstack' not in spec:

            os.chdir('src')
            # pre-processing due to the dependency to murge (git)
            copyfile('config/LINUX-GNU.in', 'config.in')
            if spec.satisfies('+murgeup'):
                # required to get murge sources "make murge_up"
                make('murge_up')
            # this file must be generated
            make('sopalin/src/murge_fortran.c')


        args = std_cmake_args
        args.remove('-DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo')

        args.extend([
            "-Wno-dev",
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
            "-DCMAKE_BUILD_TYPE=%s"      % ('Debug' if '+debug'    in spec else 'Release'),
            "-DBUILD_SHARED_LIBS=%s"     % ('ON'    if '+shared'   in spec else 'OFF'),
            "-DPASTIX_WITH_MPI=%s"       % ('ON'    if '+mpi'      in spec else 'OFF'),
            "-DPASTIX_WITH_STARPU=%s"    % ('ON'    if '+starpu'   in spec else 'OFF'),
            "-DPASTIX_WITH_CUDA=%s"      % ('ON'    if '+cuda'     in spec else 'OFF'),
            "-DPASTIX_ORDERING_METIS=%s" % ('ON'    if '+metis'    in spec else 'OFF'),
            "-DPASTIX_INT64=%s"          % ('ON'    if '+idx64'    in spec else 'OFF'),
        ])

        if spec.satisfies('@solverstack'):

            # Unfortunately we need +mpi to use it with maphys
            #if spec.satisfies('+mpi'):
            #    raise RuntimeError('@solverstack version is not available with +mpi')

            blas = spec['blas'].prefix
            blas_libs = spec['blas'].libs.ld_flags
            if spec.satisfies('+blasmt'):
                if '^mkl' in spec or '^essl' in spec or '^openblas+mt' in spec:
                    blas_libs = spec['blas'].libs.ld_flags #MT?
                else:
                    raise RuntimeError('Only ^openblas+mt, ^mkl and ^essl provide multithreaded blas.')
            args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])
            try:
                blas_flags = spec['blas'].cc_flags
            except AttributeError:
                blas_flags = ''
            args.extend(['-DBLAS_COMPILER_FLAGS=%s' % blas_flags])

            if spec.satisfies("%xl"):
                args.extend(["-DCMAKE_C_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])
                args.extend(["-DCMAKE_Fortran_FLAGS=-qstrict -qsmp -qarch=auto -qhot -qtune=auto"])
                args.extend(["-DCMAKE_CXX_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])

        else:


            args.extend([
                "-DPASTIX_WITH_MULTITHREAD=%s"  % ('ON' if '+smp'        in spec else 'OFF'),
                "-DPASTIX_DYNSCHED=%s"          % ('ON' if '+dynsched'   in spec else 'OFF'),
                "-DPASTIX_WITH_MEMORY_USAGE=%s" % ('ON' if '+memory'     in spec else 'OFF'),
                "-DPASTIX_DISTRIBUTED=%s"       % ('ON' if '^scotch+mpi' in spec else 'OFF'),
            ])

            if '^mkl-blas~shared' in spec:
                args.extend(["-DBLA_STATIC=ON"])
            if spec.satisfies('+blasmt'):
                args.extend(["-DPASTIX_BLAS_MT=ON"])

            blas = spec['blas'].prefix
            blas_libs = spec['blas'].libs.ld_flags
            if spec.satisfies('+blasmt'):
                if '^mkl' in spec or '^essl' in spec or '^openblas+mt' in spec:
                    blas_libs = spec['blas'].libs.ld_flags # MT?
                else:
                    raise RuntimeError('Only ^openblas+mt, ^mkl and ^essl provide multithreaded blas.')
            args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])

            # It seems sometimes cmake needs some help with that
            if 'mkl_intel_lp64' in blas_libs:
                args.extend(["-DBLA_VENDOR=Intel10_64lp"])

            try:
                blas_flags = spec['blas'].cc_flags
            except AttributeError:
                blas_flags = ''

            args.extend(['-DBLAS_COMPILER_FLAGS=%s' % blas_flags])

            if spec.satisfies("%xl"):
                args.extend(["-DCMAKE_C_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])
                args.extend(["-DCMAKE_Fortran_FLAGS=-qstrict -qsmp -qarch=auto -qhot -qtune=auto"])
                args.extend(["-DCMAKE_CXX_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])
                args.extend(["-DPASTIX_FM_NOCHANGE=ON"])

        return args
