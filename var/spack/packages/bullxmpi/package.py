##############################################################################
# Copyright (c) 2013, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Written by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License (as published by
# the Free Software Foundation) version 2.1 dated February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os
import spack
import sys

class Bullxmpi(Package):
    """Bull MPI commercial implementation."""
    homepage = "http://www.bull.com/"

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('BULLXMPI_DIR'):
        mpiroot=os.environ['BULLXMPI_DIR']
        if os.path.isdir(mpiroot):
            provides('mpi')

    def setup_dependent_environment(self, module, spec, dep_spec):
        bin = self.prefix.bin
        module.binmpicc  = os.path.join(bin, 'mpicc')
        module.binmpicxx = os.path.join(bin, 'mpicxx')
        module.binmpif77 = os.path.join(bin, 'mpif77')
        module.binmpif90 = os.path.join(bin, 'mpif90')

    # to use the existing version available in the environment: MPI_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BULLXMPI_DIR'):
            bullxmpiroot=os.environ['BULLXMPI_DIR']
            if os.path.isdir(bullxmpiroot):
                os.symlink(bullxmpiroot+"/bin", prefix.bin)
                os.symlink(bullxmpiroot+"/include", prefix.include)
                os.symlink(bullxmpiroot+"/lib", prefix.lib)
            else:
                sys.exit(bullxmpiroot+' directory does not exist.'+' Do you really have openmpi installed in '+bullxmpiroot+' ?')
        else:
            sys.exit('BULLXMPI_DIR is not set, you must set this environment variable to the installation path of your bullxmpi')
