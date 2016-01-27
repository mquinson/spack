from spack import *
import os
import spack
import sys
import platform

class MklBlacs(Package):
    """Intel MKL Blas, Lapack, Scalapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency (no blacs/scalapack in OSX version of MKL)
    if platform.system() != "Darwin" and os.getenv('MKLROOT'):
        mklroot=os.environ['MKLROOT']
        if os.path.isdir(mklroot):
            provides('blacs')

    variant('shared', default=True, description="Use shared library version")

    depends_on("mpi")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for mkl-blacs."""
        mkllibdir=self.spec.prefix.lib
        if spec.satisfies('+shared'):
            if spec.satisfies('%gcc'):
                module.blacslibname=["-Wl,--no-as-needed ", '-L'+mkllibdir, ' -lmkl_blacs_intelmpi_lp64']
            else:
                module.blacslibname=['-L'+mkllibdir, ' -lmkl_blacs_intelmpi_lp64']
        else:
            if '^intelmpi' in spec or '^mpich' in spec:
                module.blacslibname=[mkllibdir+'/libmkl_blacs_intelmpi_lp64.a']
            elif '^openmpi' in spec:
                module.blacslibname=[mkllibdir+'/libmkl_blacs_openmpi_lp64.a']

    def install(self, spec, prefix):
        # if spec.satisfies('+shared') and not '^intelmpi' in spec and not '^mpich' in spec:
            # sys.exit('Intel MKL does not provide dynamic blacs without intelmpi or mpich. Please use intelmpi or mpich or use ~shared to link with a static blacs library.')
        # if spec.satisfies('~shared') and not '^intelmpi' in spec and not '^mpich' in spec and not '^openmpi' in spec:
            # sys.exit('Intel MKL does not provide blacs if mpi vendor is not in the list: intelmpi, mpich, openmpi. Please use one mpi in the list.')
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                os.symlink(mklroot+"/bin", prefix.bin)
                os.symlink(mklroot+"/include", prefix.include)
                os.symlink(mklroot+"/lib/intel64", prefix.lib)
            else:
                sys.exit(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            sys.exit('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')
