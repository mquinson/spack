from spack import *
import os
import spack
import sys
import platform

class Mkl(Package):
    """Intel MKL Blas and Lapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('blas')
    provides('cblas')
    provides('lapack')
    provides('lapacke')
    provides('fft')

    variant('shared', default=True, description="Use shared library version")

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
                raise RuntimeError(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            raise RuntimeError('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for mkl-blas."""
        libdir = self.spec.prefix.lib
        opt_noasneeded="-Wl,--no-as-needed " if not platform.system() == "Darwin" else ""
        if self.spec.satisfies('%gcc'):
            if self.spec.satisfies('+shared'):
                self.spec.cc_link_mt = opt_noasneeded+"-L%s -lmkl_intel_lp64 -lmkl_core -lmkl_gnu_thread -ldl -lgomp -lpthread -lm" % libdir
                self.spec.fc_link_mt = opt_noasneeded+"-L%s -lmkl_gf_lp64 -lmkl_core -lmkl_gnu_thread -ldl -lgomp -lpthread -lm" % libdir
                self.spec.cc_link    = opt_noasneeded+"-L%s -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm" % libdir
                self.spec.fc_link    = opt_noasneeded+"-L%s -lmkl_gf_lp64 -lmkl_core -lmkl_sequential -lpthread -lm" % libdir
            else:
                self.spec.cc_link_mt ="-Wl,--start-group "+libdir+"/libmkl_intel_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_gnu_thread.a -Wl,--end-group -ldl -lgomp -lpthread -lm"
                self.spec.fc_link_mt ="-Wl,--start-group "+libdir+"/libmkl_gf_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_gnu_thread.a -Wl,--end-group -ldl -lgomp -lpthread -lm"
                self.spec.cc_link    ="-Wl,--start-group "+libdir+"/libmkl_intel_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"
                self.spec.fc_link    ="-Wl,--start-group "+libdir+"/libmkl_gf_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"
        else:
            if self.spec.satisfies('+shared'):
                self.spec.cc_link_mt = "-L%s -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -lpthread -lm" % libdir
                self.spec.cc_link    = "-L%s -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm" % libdir
            else:
                self.spec.cc_link_mt =["-Wl,--start-group "+libdir+"/libmkl_intel_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_intel_thread.a -Wl,--end-group -lpthread -lm"]
                self.spec.cc_link    =["-Wl,--start-group "+libdir+"/libmkl_intel_lp64.a "+libdir+"/libmkl_core.a "+libdir+"/libmkl_sequential.a -Wl,--end-group -lpthread -lm"]
            self.spec.fc_link_mt = self.spec.cc_link_mt
            self.spec.fc_link    = self.spec.cc_link