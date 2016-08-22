from spack import *
import os
import spack
import sys

class Hpmpi(Package):
    """HP-MPI/PlatformMPI is a proprietary implementation of
       the Message Passing Interface (MPI) standard."""
    homepage = "http://www.ibm.com/systems/fr/platformcomputing/products/mpi/index.html"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('mpi@:2.2', when='@exist')    # Platform MPI 9.1.0 supports MPI-2.2 (TODO: extract this info from mpi.h)

    def setup_dependent_environment(self, module, spec, dep_spec):
        """For dependencies, make mpicc's use spack wrapper."""
        os.environ['HPMPI_CC']  = spack_cc
        os.environ['HPMPI_CXX'] = spack_cxx
        os.environ['HPMPI_F77'] = spack_f77
        os.environ['HPMPI_F90'] = spack_fc
        # mpicc/mpiCC/mpif77 option for using multithread MPI library
        os.environ['MPI_CC_OPTIONS']  = "-lmtmpi"
        os.environ['MPI_CXX_OPTIONS'] = "-lmtmpi"
        os.environ['MPI_F77_OPTIONS'] = "-lmtmpi"
        os.environ['MPI_F90_OPTIONS'] = "-lmtmpi"

    def setup_dependent_package(self, module, dep_spec):
        self.spec.mpicc  = join_path(self.prefix.bin, 'mpicc')
        self.spec.mpicxx = join_path(self.prefix.bin, 'mpiCC')
        self.spec.mpifc  = join_path(self.prefix.bin, 'mpif90')
        self.spec.mpif77 = join_path(self.prefix.bin, 'mpif77')

    # HPMPI_DIR environment variable must be set
    def install(self, spec, prefix):
        if os.getenv('HPMPI_DIR'):
            mpiroot=os.environ['HPMPI_DIR']
            if os.path.isdir(mpiroot):
                os.symlink(mpiroot+"/lib/linux_amd64/", prefix.lib)
                os.symlink(mpiroot+"/etc/", prefix.etc)
                os.symlink(mpiroot+"/share/", prefix.share)
                os.symlink(mpiroot+"/bin/", prefix.bin)
                os.symlink(mpiroot+"/include/", prefix.include)
            else:
                raise RuntimeError(mpiroot+' directory does not exist.'+' Do you really have hpmpi installed in '+mpiroot+' ?')
        else:
            raise RuntimeError('HPMPI_DIR is not set, you must set this environment variable to the installation path of your openmpi')

