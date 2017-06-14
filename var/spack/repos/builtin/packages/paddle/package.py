##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
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
#     spack install paddle
#
# You can edit this file again by typing:
#
#     spack edit paddle
#
# See the Spack documentation for more information on packaging.
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
import os
from spack import *
import spack

def get_submodules():
    git = which('git')
    git('submodule', 'update', '--init', '--recursive')

class Paddle(Package):
    """Parallel algebraic domain decomposition for linear algebra software package."""
    # FIXME: add a proper url for your package's homepage here.
    homepage = "https://gitlab.inria.fr/solverstack/paddle"

    gitroot = "https://gitlab.inria.fr/solverstack/paddle.git"
    version('master', git=gitroot, branch='master')
    version('develop', git=gitroot, branch='develop')
    version('0.3', git=gitroot, branch='0.3')


    pkg_dir = spack.repo.dirname_for_package_name("fake")
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    
    variant("shared", default=True, description="Build a shared library")
    variant("debug", default=False, description="Enable debug symbols")
    variant("parmetis", default=False, description="Enable ParMETIS ordering")
    variant("tests", default=False, description='Enable compilation and installation of testing executables')
    
    depends_on("cmake")
    depends_on("mpi")
    depends_on("scotch+mpi")
    depends_on("parmetis",when="+parmetis")
    
    def install(self, spec, prefix):
        get_submodules()
            
        os.chdir('src')
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
            else:
                cmake_args.extend(["-DBUILD_SHARED_LIBS=OFF"])

            if spec.satisfies('+debug'):
                # Enable Debug here.
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
            else:
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])

            if spec.satisfies('+tests'):
                cmake_args.extend(["-DPADDLE_BUILD_TESTS=ON"])
            else:
                cmake_args.extend(["-DPADDLE_BUILD_TESTS=OFF"])

            if spec.satisfies('+parmetis'):
                cmake_args.extend(["-DPADDLE_ORDERING_PARMETIS=ON"])
            else:
                cmake_args.extend(["-DPADDLE_ORDERING_PARMETIS=OFF"])

            cmake(*cmake_args)
            make()
            make("install")

    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        os.symlink(maphysroot+"/bin", prefix.bin)
        os.symlink(maphysroot+"/include", prefix.include)
        os.symlink(maphysroot+"/lib", prefix.lib)
        if spec.satisfies('+examples'):
            os.symlink(maphysroot+'/examples', prefix + '/examples')
