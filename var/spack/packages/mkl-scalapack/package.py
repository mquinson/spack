from spack import *
import os
import spack
import sys

class MklScalapack(Package):
    """Intel MKL Blas, Lapack, Scalapack routines"""
    homepage = "https://software.intel.com/en-us/intel-mkl"

    pkg_dir = spack.db.dirname_for_package_name("mkl-scalapack")

    # fake tarball because we consider it is already installed
    version('0.1.0', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    provides('scalapack')

    variant('shared', default=True, description="Use shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        if os.getenv('MKLROOT'):
            mklroot=os.environ['MKLROOT']
            if os.path.isdir(mklroot):
                """Dependencies of this package will get the libraries names for mkl-scalapack."""
                mkllibdir=mklroot+"/lib/intel64/"
                if spec.satisfies('+shared'):
                    blacslib='mkl_blacs_intelmpi_lp64'
                else:
                    blacslib=mkllibdir+'libmkl_blacs_intelmpi_lp64.a'
                    if spec.satisfies('^mpich'):
                        blacslib=mkllibdir+'libmkl_blacs_lp64.a'
                    elif spec.satisfies('^mpich2'):
                        blacslib=mkllibdir+'libmkl_blacs_intelmpi_lp64.a'
                    elif spec.satisfies('^openmpi'):
                        blacslib=mkllibdir+'libmkl_blacs_openmpi_lp64.a'
                if spec.satisfies('%gcc'):
                    if spec.satisfies('+shared'):
                        module.scalapacklibname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -l"+blacslib+" -ldl -lpthread -lm"]
                        module.scalapackparlibname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_core -lmkl_gnu_thread -l"+blacslib+" -liomp5 -ldl -lpthread -lm"]
                        module.scalapacklibfortname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_gf_lp64 -lmkl_core -lmkl_sequential -l"+blacslib+" -ldl -lpthread -lm"]
                        module.scalapackparlibfortname=["-Wl,--no-as-needed -L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_gf_lp64 -lmkl_core -lmkl_gnu_thread -l"+blacslib+" -liomp5 -ldl -lpthread -lm"]

                    else:
                        module.scalapacklibname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group "+blacslib+" -lpthread -lm"]
                        module.scalapackparlibname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_intel_thread.a -Wl,--end-group "+blacslib+" -liomp5 -ldl -lpthread -lm"]
                        module.scalapacklibfortname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_gf_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group "+blacslib+" -lpthread -lm"]
                        module.scalapackparlibfortname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_gf_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_gnu_thread.a -Wl,--end-group  "+blacslib+" -liomp5 -ldl -lpthread -lm"]
                elif spec.satisfies('%icc'):
                    if spec.satisfies('+shared'):
                        module.scalapacklibname=["-L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lmkl_blacs_intelmpi_lp64 -lpthread -lm"]
                        module.scalapackparlibname=["-L"+mkllibdir+" -lmkl_scalapack_lp64 -lmkl_intel_lp64 -lmkl_core -lmkl_intel_thread -lmkl_blacs_intelmpi_lp64 -lpthread -lm"]
                    else:
                        module.scalapacklibname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_sequential.a -Wl,--end-group "+blacslib+" -lpthread -lm"]
                        module.scalapackparlibname=[mkllibdir+"libmkl_scalapack_lp64.a -Wl,--start-group "+mkllibdir+"libmkl_intel_lp64.a "+mkllibdir+"libmkl_core.a "+mkllibdir+"libmkl_intel_thread.a -Wl,--end-group "+blacslib+" -lpthread -lm"]

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
