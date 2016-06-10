from spack import *
import os
import spack
import sys
import platform

class MklScalapack(Package):
    """Intel MKL Blacs and ScaLapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('blacs')
    provides('scalapack')

    depends_on("mkl")
    depends_on("mpi")

    variant('shared', default=True, description="Use shared library version")

    def install(self, spec, prefix):
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
        """Dependencies of this package will get the link for mkl-scalapack."""
        spec = self.spec
        # scalapack lib
        if self.spec.satisfies('+shared'):
            if self.spec.satisfies('%gcc'):
                self.spec.cc_link = '-Wl,--no-as-needed -L%s -lmkl_scalapack_lp64' % spec.prefix.lib
            else:
                self.spec.cc_link='-L%s -lmkl_scalapack_lp64' % spec.prefix.lib
        else:
            self.spec.cc_link = '%s/libmkl_scalapack_lp64.a' % spec.prefix.lib
        # blacs lib
        if spec.satisfies('+shared'):
            if spec.satisfies('%gcc'):
                spec.cc_link += ' -Wl,--no-as-needed -L%s -lmkl_blacs_intelmpi_lp64' % spec.prefix.lib
            else:
                spec.cc_link += ' -L%s -lmkl_blacs_intelmpi_lp64' % spec.prefix.lib
        else:
            if '^intelmpi' in spec or '^mpich' in spec:
                spec.cc_link += ' %s/libmkl_blacs_intelmpi_lp64.a' % spec.prefix.lib
            elif '^openmpi' in spec:
                spec.cc_link += ' %s/libmkl_blacs_openmpi_lp64.a' % spec.prefix.lib