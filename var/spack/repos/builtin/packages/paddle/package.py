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
from spack import *


class Paddle(CMakePackage):
    """Parallel algebraic domain decomposition for linear algebra software package."""

    homepage = "https://gitlab.inria.fr/solverstack/paddle"
    gitroot = "https://gitlab.inria.fr/solverstack/paddle.git"

    version('master', git=gitroot, branch='master', submodules=True)
    version('develop', git=gitroot, branch='develop', submodules=True)
    version('0.3', git=gitroot, branch='0.3.1', submodules=True, preferred=True)

    variant("shared", default=True, description="Build a shared library")
    variant("debug", default=False, description="Enable debug symbols")
    variant("parmetis", default=False, description="Enable ParMETIS ordering")
    variant("tests", default=False, description='Enable compilation and installation of testing executables')

    depends_on("mpi")
    depends_on("scotch+mpi")
    depends_on("parmetis",when="+parmetis")

    root_cmakelists_dir = 'src'

    def cmake_args(self):
        spec = self.spec

        args = std_cmake_args
        args.remove('-DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo')

        args.extend([
            "-Wno-dev",
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
            "-DCMAKE_BUILD_TYPE=%s"         % ('Debug' if '+debug'   in spec else 'Release'),
            "-DBUILD_SHARED_LIBS=%s"        % ('ON'    if '+shared'  in spec else 'OFF'),
            "-DPADDLE_BUILD_TESTS=%s"       % ('ON'    if '+tests'   in spec else 'OFF'),
            "-DPADDLE_ORDERING_PARMETIS=%s" % ('ON'    if '+parmets' in spec else 'OFF')
        ])

        return args
