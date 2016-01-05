from spack import *
import os
import spack
import sys
import platform

class MklCblas(Package):
    """Intel MKL Blas and Lapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("mkl-cblas")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('MKLROOT'):
        mklroot=os.environ['MKLROOT']
        if os.path.isdir(mklroot):
            provides('cblas')

    # blas is a virtual dependency.
    depends_on('blas')

    variant('shared', default=True, description="Use shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for mkl-cblas."""
        mkllibdir=self.spec.prefix.lib
        opt_noasneeded="-Wl,--no-as-needed " if not platform.system() == "Darwin" else ""
        if spec.satisfies('+shared'):
            if spec.satisfies('%gcc'):
                module.cblaslibname=[opt_noasneeded+"-L"+mkllibdir+" -lmkl_intel_lp64"]
            else:
                module.cblaslibname=["-L"+mkllibdir+" -lmkl_intel_lp64"]
        else:
            module.cblaslibname=[mkllibdir+"/libmkl_intel_lp64.a "]

    def install(self, spec, prefix):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                mklroot=os.environ['MKLROOT']
                os.symlink(mklroot+"/bin", prefix.bin)
                os.symlink(mklroot+"/include", prefix.include)
                if platform.system() == "Darwin":
                    os.symlink(mklroot+"/lib", prefix.lib)
                else:
                    os.symlink(mklroot+"/lib/intel64", prefix.lib)
            else:
                sys.exit(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            sys.exit('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')
