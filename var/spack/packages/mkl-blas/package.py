from spack import *
import os
import spack
import sys
import platform

class MklBlas(Package):
    """Intel MKL Blas and Lapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('MKLROOT'):
        mklroot=os.environ['MKLROOT']
        if os.path.isdir(mklroot):
            provides('blas')

    variant('mt', default=False, description="Use Multithreaded version")
    variant('shared', default=True, description="Use shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for mkl-blas."""
        mkllibdir=self.spec.prefix.lib
        opt_noasneeded="-Wl,--no-as-needed " if not platform.system() == "Darwin" else ""
        if spec.satisfies('%gcc'):
            if spec.satisfies('+shared'):
                if spec.satisfies('+mt'):
                    module.blaslibname=[opt_noasneeded+"-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_gnu_thread -ldl -lgomp -lpthread -lm"]
                    module.blaslibfortname=[opt_noasneeded+"-L"+mkllibdir+" -lmkl_gf_lp64 -lmkl_core -lmkl_gnu_thread -ldl -lgomp -lpthread -lm"]
                else:
                    module.blaslibname=[opt_noasneeded+"-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
                    module.blaslibfortname=[opt_noasneeded+"-L"+mkllibdir+" -lmkl_gf_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
            else:
                if spec.satisfies('+mt'):
                    module.blaslibname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_gnu_thread.a -Wl,--end-group -ldl -lgomp -lpthread -lm"]
                    module.blaslibfortname=["-Wl,--start-group "+mkllibdir+"/libmkl_gf_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_gnu_thread.a -Wl,--end-group -ldl -lgomp -lpthread -lm"]
                else:
                    module.blaslibname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
                    module.blaslibfortname=["-Wl,--start-group "+mkllibdir+"/libmkl_gf_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
        else:
            if spec.satisfies('+shared'):
                if spec.satisfies('+mt'):
                    module.blaslibname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -lpthread -lm"]
                    module.blaslibfortname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -lpthread -lm"]
                else:
                    module.blaslibname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]
                    module.blaslibfortname=["-L"+mkllibdir+" -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm"]

            else:
                if spec.satisfies('+mt'):
                    module.blaslibname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_intel_thread.a -Wl,--end-group -lpthread -lm"]
                    module.blaslibfortname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_intel_thread.a -Wl,--end-group -lpthread -lm"]
                else:
                    module.blaslibname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
                    module.blaslibfortname=["-Wl,--start-group "+mkllibdir+"/libmkl_intel_lp64.a "+mkllibdir+"/libmkl_core.a "+mkllibdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"]

    def install(self, spec, prefix):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
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
