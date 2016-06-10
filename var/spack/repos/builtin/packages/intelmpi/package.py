from spack import *
import os
import spack
import sys

class Intelmpi(Package):
    """Intel's implementation of the
       the Message Passing Interface (MPI) standard."""
    homepage = "https://software.intel.com/en-us/intel-mpi-library"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('I_MPI_ROOT'):
        mpiroot=os.environ['I_MPI_ROOT']
        if os.path.isdir(mpiroot):
            provides('mpi')

    def setup_dependent_package(self, module, dep_spec):
        if self.spec.satisfies('%intel'):
            self.spec.mpicc  = join_path(self.prefix.bin, 'mpiicc')
            self.spec.mpicxx = join_path(self.prefix.bin, 'mpiicpc')
            self.spec.mpifc  = join_path(self.prefix.bin, 'mpiifort')
            self.spec.mpif77 = join_path(self.prefix.bin, 'mpiifort')
        else:
            self.spec.mpicc  = join_path(self.prefix.bin, 'mpicc')
            self.spec.mpicxx = join_path(self.prefix.bin, 'mpicxx')
            self.spec.mpifc  = join_path(self.prefix.bin, 'mpif90')
            self.spec.mpif77 = join_path(self.prefix.bin, 'mpif77')

    def install(self, spec, prefix):
        mpiroot=os.environ['I_MPI_ROOT']
        if os.path.isdir(mpiroot):
            os.symlink(mpiroot+"/intel64/bin", prefix.bin)
            os.symlink(mpiroot+"/intel64/etc", prefix.etc)
            os.symlink(mpiroot+"/intel64/include", prefix.include)
            os.symlink(mpiroot+"/intel64/lib", prefix.lib)
        else:
            raise RuntimeError(mpiroot+' directory does not exist.'+' Do you really have intelmpi installed in '+mpiroot+' ?')
