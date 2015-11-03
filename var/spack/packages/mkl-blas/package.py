from spack import *
import os
import spack
import sys

class MklBlas(Package):
    """Intel MKL Blas and Lapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("mkl-blas")

    # fake tarball because we consider it is already installed
    version('0.1.0', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('MKLROOT'):
        mklroot=os.environ['MKLROOT']
        if os.path.isdir(mklroot):
            provides('blas')

    variant('shared', default=True, description="Use shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                """Dependencies of this package will get the libraries names for mkl-blas."""
                mkllibdir=mklroot+"/lib/intel64/"
                if spec.satisfies('%gcc'):
                    if spec.satisfies('+shared'):
                        module.blaslibname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
                        module.blasparlibname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -ldl -liomp5 -lpthread -lm"]
                        module.blaslibfortname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_gf_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
                        module.blasparlibfortname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_gf_lp64 -lmkl_core -lmkl_intel_thread -ldl -liomp5 -lpthread -lm"]
                    else:
                        module.blaslibname=["-Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
                        module.blasparlibname=["-Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_intel_thread.a -Wl,--end-group -ldl -liomp5 -lpthread -lm"]
                        module.blaslibfortname=["-Wl,--start-group "+mkllibdir+"libmkl_gf_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
                        module.blasparlibfortname=["-Wl,--start-group "+mkllibdir+"libmkl_gf_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_intel_thread.a -Wl,--end-group -ldl -liomp5 -lpthread -lm"]
                elif spec.satisfies('%icc'):
                    if spec.satisfies('+shared'):
                        module.blaslibname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
                        module.blasparlibname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -lpthread -lm"]
                    else:
                        module.blaslibname=["-Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
                        module.blasparlibname=["-Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_intel_thread.a -Wl,--end-group -lpthread -lm"]

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
