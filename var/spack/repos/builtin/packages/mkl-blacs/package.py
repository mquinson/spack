from spack import *
import os
import spack
import sys
import platform

class MklBlacs(Package):
    """Intel MKL Blas, Lapack, Scalapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('blacs')

    depends_on("mpi")

    variant('shared', default=True, description="Use shared library version")

    def install(self, spec, prefix):
        # if spec.satisfies('+shared') and not '^intelmpi' in spec and not '^mpich' in spec:
            # raise RuntimeError('Intel MKL does not provide dynamic blacs without intelmpi or mpich. Please use intelmpi or mpich or use ~shared to link with a static blacs library.')
        # if spec.satisfies('~shared') and not '^intelmpi' in spec and not '^mpich' in spec and not '^openmpi' in spec:
            # raise RuntimeError('Intel MKL does not provide blacs if mpi vendor is not in the list: intelmpi, mpich, openmpi. Please use one mpi in the list.')
        if platform.system() == "Darwin":
            raise RuntimeError('No blacs/scalapack in OSX version of MKL')
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                os.symlink(mklroot+"/bin", prefix.bin)
                os.symlink(mklroot+"/include", prefix.include)
                os.symlink(mklroot+"/lib/intel64", prefix.lib)
            else:
                raise RuntimeError(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            raise RuntimeError('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for mkl-blacs."""
        spec = self.spec
        if spec.satisfies('+shared'):
            if spec.satisfies('%gcc'):
                spec.cc_link = '-Wl,--no-as-needed -L%s -lmkl_blacs_intelmpi_lp64' % spec.prefix.lib
            else:
                spec.cc_link = '-L%s -lmkl_blacs_intelmpi_lp64' % spec.prefix.lib
        else:
            if '^intelmpi' in spec or '^mpich' in spec:
                spec.cc_link = '%s/libmkl_blacs_intelmpi_lp64.a' % spec.prefix.lib
            elif '^openmpi' in spec:
                spec.cc_link = '%s/libmkl_blacs_openmpi_lp64.a' % spec.prefix.lib