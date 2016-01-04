from spack import *
import os
import spack
import sys

class MklScalapack(Package):
    """Intel MKL Blas, Lapack, Scalapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("mkl-scalapack")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('MKLROOT'):
        mklroot=os.environ['MKLROOT']
        if os.path.isdir(mklroot):
            provides('scalapack')

    variant('shared', default=True, description="Use shared library version")

    depends_on("blacs")
    depends_on("blas")
    depends_on("lapack")

    def setup_dependent_environment(self, module, spec, dep_spec):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                """Dependencies of this package will get the libraries names for mkl-scalapack."""
                mkllibdir=mklroot+"/lib/intel64/"
                if spec.satisfies('+shared'):
                    if spec.satisfies('%gcc'):
                        module.scalapacklibname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_scalapack_lp64"]
                    else:
                        module.scalapacklibname=["-L"+mkllibdir+" -lmkl_scalapack_lp64"]
                else:
                    module.scalapacklibname=[mkllibdir+"libmkl_scalapack_lp64.a"]

    def install(self, spec, prefix):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                mklroot=os.environ['MKLROOT']
                os.symlink(mklroot+"/bin", prefix.bin)
                os.symlink(mklroot+"/include", prefix.include)
                os.symlink(mklroot+"/lib/intel64", prefix.lib)
            else:
                sys.exit(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            sys.exit('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')
