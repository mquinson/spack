from spack import *
import glob
import os
from subprocess import call
import sys

class Scotch(Package):
    """Scotch is a software package for graph and mesh/hypergraph
       partitioning, graph clustering, and sparse matrix ordering."""
    homepage = "http://www.labri.fr/perso/pelegrin/scotch/"
    url      = "http://gforge.inria.fr/frs/download.php/file/34099/scotch_6.0.3.tar.gz"
    list_url = "http://gforge.inria.fr/frs/?group_id=248"

    version('6.0.3', '10b0cc0f184de2de99859eafaca83cfc')
    version('6.0.4', 'd58b825eb95e1db77efe8c6ff42d329f',
            url='https://gforge.inria.fr/frs/download.php/file/34618/scotch_6.0.4.tar.gz')

    variant('mac', default=False, description='Patch the configuration to make it MAC OS X compatible')
    variant('mpi', default=False, description='Enable MPI support')
    variant('pthread', default=True, description='Enable multithread with pthread')
    variant('shared', default=False, description='Build SCOTCH as a shared library')

    depends_on('mpi', when='+mpi')

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

            if spec.satisfies('+mac'):
                filter_file(r'-lrt', '', *makefiles)

    def install(self, spec, prefix):
        # Currently support gcc and icc on x86_64 (maybe others with
        # vanilla makefile)
        makefile = 'Make.inc/Makefile.inc.x86-64_pc_linux2'
        if spec.satisfies('%icc'):
            makefile += '.icc'

        with working_dir('src'):
            mf = FileFilter(makefile)
            if spec.satisfies('+shared'):
                mf.filter('CFLAGS       =', 'CFLAGS     = -fPIC')
            if spec.satisfies('@5'):
                mf.filter('LDFLAGS\s*=', 'LDFLAGS = -pthread ')

            force_symlink(makefile, 'Makefile.inc')
            make('scotch')
            if not spec.satisfies('@5'):
                make('esmumps')
            if spec.satisfies('+mpi'):
                make('ptscotch')
                if not spec.satisfies('@5'):
                    make('ptesmumps',parallel=False)

        install_tree('bin', prefix.bin)
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        install_tree('man/man1', prefix.share_man1)
