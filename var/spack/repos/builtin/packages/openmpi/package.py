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
import os
import spack
import sys
from spack import *



def _verbs_dir():
    """
    Try to find the directory where the OpenFabrics verbs package is
    installed. Return None if not found.
    """
    try:
        # Try to locate Verbs by looking for a utility in the path
        ibv_devices = which("ibv_devices")
        # Run it (silently) to ensure it works
        ibv_devices(output=str, error=str)
        # Get path to executable
        path = ibv_devices.exe[0]
        # Remove executable name and "bin" directory
        path = os.path.dirname(path)
        path = os.path.dirname(path)
        return path
    except:
        return None


class Openmpi(Package):
    """Open MPI is a project combining technologies and resources from
       several other projects (FT-MPI, LA-MPI, LAM/MPI, and PACX-MPI)
       in order to build the best MPI library available. A completely
       new MPI-2 compliant implementation, Open MPI offers advantages
       for system and software vendors, application developers and
       computer science researchers.
    """

    homepage = "http://www.open-mpi.org"
    url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.1.tar.bz2"
    list_url = "http://www.open-mpi.org/software/ompi/"
    list_depth = 3

    version('2.0.1', '6f78155bd7203039d2448390f3b51c96',
            url = "http://www.open-mpi.org/software/ompi/v2.0/downloads/openmpi-2.0.1.tar.bz2")
    version('2.0.0', 'cdacc800cb4ce690c1f1273cb6366674',
            url = "http://www.open-mpi.org/software/ompi/v2.0/downloads/openmpi-2.0.0.tar.bz2")
    version('1.10.4', '9d2375835c5bc5c184ecdeb76c7c78ac',
            url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.4.tar.bz2")
    version('1.10.3', 'e2fe4513200e2aaa1500b762342c674b',
            url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.3.tar.bz2")
    version('1.10.2', 'b2f43d9635d2d52826e5ef9feb97fd4c',
            url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.2.tar.bz2")
    version('1.10.1', 'f0fcd77ed345b7eafb431968124ba16e',
            url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.1.tar.bz2")
    version('1.10.0', '280cf952de68369cebaca886c5ce0304',
            url = "http://www.open-mpi.org/software/ompi/v1.10/downloads/openmpi-1.10.0.tar.bz2")
    version('1.8.8', '0dab8e602372da1425e9242ae37faf8c',
            url = 'http://www.open-mpi.org/software/ompi/v1.8/downloads/openmpi-1.8.8.tar.bz2')
    version('1.6.5', '03aed2a4aa4d0b27196962a2a65fc475',
            url = "http://www.open-mpi.org/software/ompi/v1.6/downloads/openmpi-1.6.5.tar.bz2")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    patch('ad_lustre_rwcontig_open_source.patch', when="@1.6.5")
    patch('llnl-platforms.patch', when="@1.6.5")
    patch('configure.patch_16', when="@1.6.5")
    patch('configure.patch_18', when="@1.8.8")
    patch('configure.patch', when="@1.10.0:1.10.1")

    variant('psm', default=False, description='Build support for the PSM library.')
    variant('psm2', default=False, description='Build support for the Intel PSM2 library.')
    variant('pmi', default=False, description='Build support for PMI-based launchers')
    variant('verbs', default=_verbs_dir() is not None, description='Build support for OpenFabrics verbs.')
    variant('mxm', default=False, description='Build Mellanox Messaging support')

    variant('thread_multiple', default=True, description='Enable MPI_THREAD_MULTIPLE support')
    variant('cuda', default=False, description='Enable CUDA support')

    # TODO : variant support for alps, loadleveler  is missing
    variant('tm', default=False, description='Build TM (Torque, PBSPro, and compatible) support')
    variant('slurm', default=False, description='Build SLURM scheduler component')

    variant('sqlite3', default=False, description='Build sqlite3 support')

    variant('vt', default=True, description='Build support for contributed package vt')

    variant('debug', default=False, description='Enable debug symbols')

    provides('mpi@:2.2', when='@1.6.5')
    provides('mpi@:3.0', when='@1.7.5:')
    provides('mpi', when='@exist')

    depends_on('hwloc')
    depends_on('sqlite', when='+sqlite3')
    depends_on('cuda', when='+cuda')

    def url_for_version(self, version):
        return "http://www.open-mpi.org/software/ompi/v%s/downloads/openmpi-%s.tar.bz2" % (version.up_to(2), version)


    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('OMPI_CC', spack_cc)
        spack_env.set('OMPI_CXX', spack_cxx)
        spack_env.set('OMPI_FC', spack_fc)
        spack_env.set('OMPI_F77', spack_f77)

    def setup_dependent_package(self, module, dep_spec):
        self.spec.mpicc  = join_path(self.prefix.bin, 'mpicc')
        self.spec.mpicxx = join_path(self.prefix.bin, 'mpic++')
        self.spec.mpifc  = join_path(self.prefix.bin, 'mpif90')
        self.spec.mpif77 = join_path(self.prefix.bin, 'mpif77')

    @property
    def verbs(self):
        # Up through version 1.6, this option was previously named --with-openib
        if self.spec.satisfies('@:1.6'):
            return 'openib'
        # In version 1.7, it was renamed to be --with-verbs
        elif self.spec.satisfies('@1.7:'):
            return 'verbs'

    def install(self, spec, prefix):
        config_args = ["--prefix=%s" % prefix,
                       "--with-hwloc=%s" % spec['hwloc'].prefix,
                       "--enable-shared",
                       "--enable-static"]
        # Variant based arguments
        config_args.extend([
            # Schedulers
            '--with-tm' if '+tm' in spec else '--without-tm',
            '--with-slurm' if '+slurm' in spec else '--without-slurm',
            # Fabrics
            '--with-psm' if '+psm' in spec else '--without-psm',
            '--with-psm2' if '+psm2' in spec else '--without-psm2',
            '--with-mxm' if '+mxm' in spec else '--without-mxm',
            # Other options
            '--enable-mpi-thread-multiple' if '+thread_multiple' in spec else '--disable-mpi-thread-multiple',
            '--with-pmi' if '+pmi' in spec else '--without-pmi',
            '--with-sqlite3' if '+sqlite3' in spec else '--without-sqlite3',
            '--enable-vt' if '+vt' in spec else '--disable-vt',
            '--with-cuda=%s' % spec['cuda'].prefix if '+cuda' in spec else '--without-cuda'
        ])
        if '+verbs' in spec:
            path = _verbs_dir()
            if path is not None:
                config_args.append('--with-%s=%s' % (self.verbs, path))
            else:
                config_args.append('--with-%s' % self.verbs)
        else:
            config_args.append('--without-%s' % self.verbs)

        # TODO: use variants for this, e.g. +lanl, +llnl, etc.
        # use this for LANL builds, but for LLNL builds, we need:
        #     "--with-platform=contrib/platform/llnl/optimized"
        if self.version == ver("1.6.5") and '+lanl' in spec:
            config_args.append("--with-platform=contrib/platform/lanl/tlcc2/optimized-nopanasas")

        if not self.compiler.f77 and not self.compiler.fc:
            config_args.append("--enable-mpi-fortran=no")

        if '+debug' in spec :
            config_args.append("--enable-debug")

        # With intel 16, the 'deprecated' warnings in mpi.h triggers compilation error when building user application, so we disable...
        if '%intel' in spec :
            config_args.append("--disable-mpi-interface-warning")

        configure(*config_args)
        make()
        make("install")

        self.filter_compilers()

    # to use the existing version available in the environment: MPI_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('OPENMPI_DIR'):
            mpiroot=os.environ['OPENMPI_DIR']
            if os.path.isdir(mpiroot):
                os.symlink(mpiroot+"/bin", prefix.bin)
                os.symlink(mpiroot+"/include", prefix.include)
                os.symlink(mpiroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(mpiroot+' directory does not exist.'+' Do you really have openmpi installed in '+mpiroot+' ?')
        else:
            raise RuntimeError('OPENMPI_DIR is not set, you must set this environment variable to the installation path of your openmpi')

    def filter_compilers(self):
        """Run after install to make the MPI compilers use the
           compilers that Spack built the package with.

           If this isn't done, they'll have CC, CXX and FC set
           to Spack's generic cc, c++ and f90.  We want them to
           be bound to whatever compiler they were built with.
        """
        kwargs = {'ignore_absent': True, 'backup': False, 'string': False}
        dir = os.path.join(self.prefix, 'share/openmpi/')

        cc_wrappers = ['mpicc-vt-wrapper-data.txt', 'mpicc-wrapper-data.txt',
                       'ortecc-wrapper-data.txt', 'shmemcc-wrapper-data.txt']

        cxx_wrappers = ['mpic++-vt-wrapper-data.txt', 'mpic++-wrapper-data.txt',
                        'ortec++-wrapper-data.txt']

        fc_wrappers = ['mpifort-vt-wrapper-data.txt',
                       'mpifort-wrapper-data.txt', 'shmemfort-wrapper-data.txt']

        for wrapper in cc_wrappers:
            filter_file('compiler=.*', 'compiler=%s' % self.compiler.cc,
                        os.path.join(dir, wrapper), **kwargs)

        for wrapper in cxx_wrappers:
            filter_file('compiler=.*', 'compiler=%s' % self.compiler.cxx,
                        os.path.join(dir, wrapper), **kwargs)

        for wrapper in fc_wrappers:
            filter_file('compiler=.*', 'compiler=%s' % self.compiler.fc,
                        os.path.join(dir, wrapper), **kwargs)

        # These are symlinks in newer versions, so check that here
        f77_wrappers = ['mpif77-vt-wrapper-data.txt', 'mpif77-wrapper-data.txt']
        f90_wrappers = ['mpif90-vt-wrapper-data.txt', 'mpif90-wrapper-data.txt']

        for wrapper in f77_wrappers:
            path = os.path.join(dir, wrapper)
            if not os.path.islink(path):
                filter_file('compiler=.*', 'compiler=%s' % self.compiler.f77,
                            path, **kwargs)
        for wrapper in f90_wrappers:
            path = os.path.join(dir, wrapper)
            if not os.path.islink(path):
                filter_file('compiler=.*', 'compiler=%s' % self.compiler.fc,
                            path, **kwargs)
