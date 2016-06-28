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
    provides('tmglib')
    provides('lapacke')
    provides('fft')

    variant('32bit', default=False, description="Use 32-bit version")
    variant('int64', default=False, description="Use 64-bit integer version")
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
                    if spec.satisfies('+32bit'):
                        os.symlink(mklroot+"/lib/ia32", prefix.lib)
                    else:
                        os.symlink(mklroot+"/lib/intel64", prefix.lib)
            else:
                raise RuntimeError(mklroot+' directory does not exist.'+' Do you really have Intel MKL installed in '+mklroot+' ?')
        else:
            raise RuntimeError('MKLROOT environment variable does not exist. Please set MKLROOT to use the Intel MKL')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for mkl-blas."""
        spec = self.spec
        libdir = self.spec.prefix.lib

        ## define C/Fortran flags
        spec.cc_flags    = ""
        spec.fc_flags    = ""

        # 32/64 bits pointers option
        if spec.satisfies('%gcc'):
            spec.cc_flags = "-m32" if spec.satisfies('+32bit') else "-m64"

        # int 64 bits options
        if spec.satisfies('+int64'):
            spec.cc_flags = spec.cc_flags + " -DMKL_ILP64"
            if spec.satisfies('%gcc'):
                spec.fc_flags = spec.fc_flags + " -fdefault-integer-8"
            elif spec.satisfies('%intel'):
                spec.fc_flags = spec.fc_flags + " -i8"

        # path to headers
        spec.cc_flags = spec.cc_flags+" -I${MKLROOT}/include"

        spec.cc_flags_mt = spec.cc_flags
        spec.fc_flags_mt = spec.fc_flags
        if spec.satisfies('%intel'):
            spec.cc_flags_mt = "-qopenmp " + spec.cc_flags_mt
            spec.fc_flags_mt = "-qopenmp " + spec.fc_flags_mt

        # define mkl libs
        if spec.satisfies('+32bit'):
            mkl_lib    = "mkl_intel"
            mkl_lib_gf = "mkl_gf"
        else:
            if spec.satisfies('+int64'):
                mkl_lib    = "mkl_intel_ilp64"
                mkl_lib_gf = "mkl_gf_ilp64" if spec.satisfies('%gcc') else "mkl_intel_ilp64"
            else:
                mkl_lib    = "mkl_intel_lp64"
                mkl_lib_gf = "mkl_gf_lp64" if spec.satisfies('%gcc') else "mkl_intel_lp64"

        mkl_core = "mkl_core"

        # define mkl thread and other libs
        mkl_seq = "mkl_sequential"
        if spec.satisfies('%gcc'):
            mkl_thread = "mkl_gnu_thread"
        else:
            mkl_thread = "mkl_intel_thread"
        mkl_thread_others = "-liomp5"
        mkl_others  = "-lpthread -lm -ldl"
        if not platform.system() == "Darwin":
            start_group = "-Wl,--start-group"
            end_group   = "-Wl,--end-group"
        else:
            start_group = ""
            end_group   = ""
        # option required by gcc in dynamic
        opt_noasneeded="-Wl,--no-as-needed " if not platform.system() == "Darwin" else ""

        if spec.satisfies('+shared'):
            spec.cc_link = "%s -L%s -l%s -l%s -l%s %s" % \
            (opt_noasneeded, libdir, mkl_lib, mkl_core, mkl_seq, mkl_others)
            spec.cc_link_mt = "%s -L%s -l%s -l%s -l%s %s %s" % \
            (opt_noasneeded, libdir, mkl_lib, mkl_core, mkl_thread, mkl_thread_others, mkl_others)
            spec.fc_link = "%s -L%s -l%s -l%s -l%s %s" % \
            (opt_noasneeded, libdir, mkl_lib_gf, mkl_core, mkl_seq, mkl_others)
            spec.fc_link_mt = "%s -L%s -l%s -l%s -l%s %s %s" % \
            (opt_noasneeded, libdir, mkl_lib_gf, mkl_core, mkl_thread, mkl_thread_others, mkl_others)
        else:
            spec.cc_link = "%s %s/lib%s.a %s/lib%s.a %s/lib%s.a %s %s" % \
            (start_group, libdir, mkl_lib, libdir, mkl_core, libdir, mkl_seq, end_group, mkl_others)
            spec.cc_link_mt = "%s %s/lib%s.a %s/lib%s.a %s/lib%s.a %s %s %s" % \
            (start_group, libdir, mkl_lib, libdir, mkl_core, libdir, mkl_thread, end_group, mkl_thread_others, mkl_others)
            spec.fc_link = spec.cc_link
            spec.fc_link_mt = spec.cc_link_mt