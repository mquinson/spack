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
from spack import *
import os
import platform
import spack

class Hwloc(Package):
    """The Portable Hardware Locality (hwloc) software package
       provides a portable abstraction (across OS, versions,
       architectures, ...) of the hierarchical topology of modern
       architectures, including NUMA memory nodes, sockets, shared
       caches, cores and simultaneous multithreading. It also gathers
       various system attributes such as cache and memory information
       as well as the locality of I/O devices such as network
       interfaces, InfiniBand HCAs or GPUs. It primarily aims at
       helping applications with gathering information about modern
       computing hardware so as to exploit it accordingly and
       efficiently."""
    homepage = "http://www.open-mpi.org/projects/hwloc/"
    url      = "http://www.open-mpi.org/software/hwloc/v1.9/downloads/hwloc-1.9.tar.gz"
    list_url = "http://www.open-mpi.org/software/hwloc/"
    list_depth = 3
    version('1.11.3', '42d1d6c5c237069813cd28292629fc39',
            url='https://www.open-mpi.org/software/hwloc/v1.11/downloads/hwloc-1.11.3.tar.bz2')
    version('1.11.2', '486169cbe111cdea57be12638828ebbf',
            url='http://www.open-mpi.org/software/hwloc/v1.11/downloads/hwloc-1.11.2.tar.bz2')
    version('1.11.1', '002742efd3a8431f98d6315365a2b543',
            url='http://www.open-mpi.org/software/hwloc/v1.11/downloads/hwloc-1.11.1.tar.bz2')
    version('1.11.0', '150a6a0b7a136bae5443e9c2cf8f316c',
            url='http://www.open-mpi.org/software/hwloc/v1.11/downloads/hwloc-1.11.0.tar.gz')
    version('1.10.1', '27f2966df120a74df19dc244d5340107',
            url='http://www.open-mpi.org/software/hwloc/v1.10/downloads/hwloc-1.10.1.tar.gz')
    version('1.9', '1f9f9155682fe8946a97c08896109508',
            url="http://www.open-mpi.org/software/hwloc/v1.9/downloads/hwloc-1.9.tar.gz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')
    depends_on('libpciaccess')

    def url_for_version(self, version):
        return "http://www.open-mpi.org/software/hwloc/v%s/downloads/hwloc-%s.tar.gz" % (version.up_to(2), version)

    def install(self, spec, prefix):

        sys_name = platform.system()
        if sys_name == 'Darwin':
            configure("--prefix=%s" % prefix , "--without-x")
        else:
            configure("--prefix=%s" % prefix)

        make()
        make("install")

    # to use the existing version available in the environment: HWLOC_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('HWLOC_DIR'):
            hwlocroot=os.environ['HWLOC_DIR']
            if os.path.isdir(hwlocroot):
                os.symlink(hwlocroot+"/bin", prefix.bin)
                os.symlink(hwlocroot+"/include", prefix.include)
                os.symlink(hwlocroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(hwlocroot+' directory does not exist.'+' Do you really have openmpi installed in '+hwlocroot+' ?')
        else:
            raise RuntimeError('HWLOC_DIR is not set, you must set this environment variable to the installation path of your hwloc')
