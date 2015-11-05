from spack import *
import glob
import os
from subprocess import call
import sys
import platform

class Scotch(Package):
    """Scotch is a software package for graph and mesh/hypergraph
       partitioning, graph clustering, and sparse matrix ordering."""
    homepage = "http://www.labri.fr/perso/pelegrin/scotch/"
    url      = "http://gforge.inria.fr/frs/download.php/file/34099/scotch_6.0.3.tar.gz"
    list_url = "http://gforge.inria.fr/frs/?group_id=248"

    version('6.0.3', '10b0cc0f184de2de99859eafaca83cfc')
    version('6.0.4', 'd58b825eb95e1db77efe8c6ff42d329f',
            url='https://gforge.inria.fr/frs/download.php/file/34618/scotch_6.0.4.tar.gz')
    version('5.1.11', 'c00a886895b3895529814303afe0d74e',
            url='https://gforge.inria.fr/frs/download.php/28044/scotch_5.1.11_esmumps.tar.gz')

    variant('esmumps', default=False, description='Enable esmumps')
    variant('mpi', default=False, description='Enable MPI support')
    variant('pthread', default=True, description='Enable multithread with pthread')
    variant('shared', default=True, description='Build SCOTCH as a shared library')

    depends_on('mpi', when='+mpi')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for Scotch."""
        libdir = self.spec.prefix.lib
        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                scotchlibname=[os.path.join(libdir, "libscotch.dylib")]
                scotcherrlibname=[os.path.join(libdir, "libscotcherr.dylib")]
                scotcherrexitlibname=[os.path.join(libdir, "libscotcherrexit.dylib")]
                ptscotchlibname=[os.path.join(libdir, "libptscotch.dylib")]
                ptscotcherrlibname=[os.path.join(libdir, "libptscotcherr.dylib")]
                ptscotcherrexitlibname=[os.path.join(libdir, "libptscotcherrexit.dylib")]
                esmumpslibname=[os.path.join(libdir, "libesmumps.dylib")]
                ptesmumpslibname=[os.path.join(libdir, "libptesmumps.dylib")]
            else:
                scotchlibname=[os.path.join(libdir, "libscotch.so")]
                scotcherrlibname=[os.path.join(libdir, "libscotcherr.so")]
                scotcherrexitlibname=[os.path.join(libdir, "libscotcherrexit.so")]
                ptscotchlibname=[os.path.join(libdir, "libptscotch.so")]
                ptscotcherrlibname=[os.path.join(libdir, "libptscotcherr.so")]
                ptscotcherrexitlibname=[os.path.join(libdir, "libptscotcherrexit.so")]
                esmumpslibname=[os.path.join(libdir, "libesmumps.so")]
                ptesmumpslibname=[os.path.join(libdir, "libptesmumps.so")]
        else:
            scotchlibname=[os.path.join(libdir, "libscotch.a")]
            scotcherrlibname=[os.path.join(libdir, "libscotcherr.a")]
            scotcherrexitlibname=[os.path.join(libdir, "libscotcherrexit.a")]
            ptscotchlibname=[os.path.join(libdir, "libptscotch.a")]
            ptscotcherrlibname=[os.path.join(libdir, "libptscotcherr.a")]
            ptscotcherrexitlibname=[os.path.join(libdir, "libptscotcherrexit.a")]
            esmumpslibname=[os.path.join(libdir, "libesmumps.a")]
            ptesmumpslibname=[os.path.join(libdir, "libptesmumps.a")]

        otherlibs=["-lz", "-lm", "-lpthread"]
        if platform.system() == 'Linux':
            otherlibs+=["-lrt"]

        module.scotchlibname = []
        if spec.satisfies('+esmumps'):
            if spec.satisfies('+mpi'):
                module.scotchlibname+=ptesmumpslibname
                module.scotchlibname+=ptscotchlibname
                module.scotchlibname+=ptscotcherrlibname
            module.scotchlibname+=esmumpslibname
        else:
            if spec.satisfies('+mpi'):
                module.scotchlibname+=ptscotchlibname
                module.scotchlibname+=ptscotcherrlibname
        module.scotchlibname+=scotchlibname
        module.scotchlibname+=scotcherrlibname
        module.scotchlibname+=otherlibs

    def patch(self):
        if self.spec.satisfies('~pthread') and self.spec.satisfies('@6.0.4'):
            sys.exit('Error: SCOTCH 6.0.4 cannot compile without pthread... :(')
        with working_dir('src/Make.inc'):
            spec = self.spec
            makefiles = glob.glob('Makefile.inc.x86-64_pc_linux2*')
            filter_file(r'^CCS\s*=.*$', 'CCS = cc', *makefiles)
            filter_file(r'^CCD\s*=.*$', 'CCD = cc', *makefiles)
            if spec.satisfies('%icc'):
                call(["cp", "Makefile.inc.x86-64_pc_linux2.shlib", "Makefile.inc.x86-64_pc_linux2.shlib.icc"])
                filter_file(r'^CLIBFLAGS\s*=.*$', 'CLIBFLAGS = -shared -fpic', *makefiles)
            elif spec.satisfies('+shared'):
                filter_file(r'^CLIBFLAGS\s*=.*$', 'CLIBFLAGS = -shared -fpic', *makefiles)

            if spec.satisfies('+pthread'):
                filter_file(r'-DCOMMON_PTHREAD', '-DSCOTCH_DETERMINISTIC -DCOMMON_PTHREAD -DCOMMON_PTHREAD_BARRIER -DCOMMON_TIMING_OLD', *makefiles)
            else:
                filter_file(r'-DCOMMON_PTHREAD', '-DSCOTCH_DETERMINISTIC -DCOMMON_TIMING_OLD', *makefiles)
                filter_file(r'-DSCOTCH_PTHREAD', '', *makefiles)

            if platform.system() == 'Darwin':
                filter_file(r'-lrt', '', *makefiles)

    def install(self, spec, prefix):
        # Currently support gcc and icc on x86_64 (maybe others with
        # vanilla makefile)
        if spec.satisfies('@6:+shared'):
            makefile = 'Make.inc/Makefile.inc.x86-64_pc_linux2.shlib'
        else:
            makefile = 'Make.inc/Makefile.inc.x86-64_pc_linux2'
        if spec.satisfies('%icc'):
            makefile += '.icc'

        with working_dir('src'):
            mf = FileFilter(makefile)
            if spec.satisfies('+shared'):
                mf.filter('CFLAGS\s*=', 'CFLAGS     = -fPIC')
            if spec.satisfies('@5'):
                mf.filter('LDFLAGS\s*=', 'LDFLAGS = -pthread ')
            if spec.satisfies('+shared'):
                mf.filter('^AR\s*=.*', 'AR=$(CC) ')
                mf.filter('^ARFLAGS\s*=.*', 'ARFLAGS=-shared -o')
                mf.filter('^RANLIB\s*=.*', 'RANLIB=echo')
                mf.filter('^LIB\s*=.*', 'LIB=.so')

            force_symlink(makefile, 'Makefile.inc')
            make('scotch')
            if spec.satisfies('@6:') and spec.satisfies('+esmumps'):
                make('esmumps')
            if spec.satisfies('+mpi'):
                make('ptscotch')
                if spec.satisfies('@6:') and spec.satisfies('+esmumps'):
                    make('ptesmumps',parallel=False)

        install_tree('bin', prefix.bin)
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        install_tree('man/man1', prefix.share_man1)
