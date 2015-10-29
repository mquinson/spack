from spack import *
import os
import spack

class Hpmpi(Package):
    """HP-MPI/PlatformMPI is a proprietary implementation of
       the Message Passing Interface (MPI) standard."""
    homepage = "http://www.ibm.com/systems/fr/platformcomputing/products/mpi/index.html"

    pkg_dir = spack.db.dirname_for_package_name("hpmpi")

    version('9.1.0', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('mpi@:2.2')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """For dependencies, make mpicc's use spack wrapper."""
        os.environ['HPMPI_CC']  = 'cc'
        os.environ['HPMPI_CXX'] = 'c++'
        os.environ['HPMPI_F77'] = 'f77'
        os.environ['HPMPI_F90'] = 'f90'
        # mpicc/mpiCC/mpif77 option for using multithread MPI library
        os.environ['MPI_CC_OPTIONS']  = "-lmtmpi"
        os.environ['MPI_CXX_OPTIONS'] = "-lmtmpi"
        os.environ['MPI_F77_OPTIONS'] = "-lmtmpi"
        os.environ['MPI_F90_OPTIONS'] = "-lmtmpi"

    def install(self, spec, prefix):
        os.environ['MPI_ROOT'] = "/opt/hpmpi/"
	os.symlink("/opt/hpmpi/lib/linux_amd64/", prefix.lib)
        os.symlink("/opt/hpmpi/etc/", prefix.etc)
        os.symlink("/opt/hpmpi/share/", prefix.share)
        os.symlink("/opt/hpmpi/bin/", prefix.bin)
        os.symlink("/opt/hpmpi/include/", prefix.include)
