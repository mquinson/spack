from spack import *
import glob
import os
from subprocess import call

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
    variant('shared', default=False, description='Build SCOTCH as a shared library')

    depends_on('mpi', when='+mpi')

    def patch(self):
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

            filter_file(r'-DCOMMON_PTHREAD', '-DSCOTCH_DETERMINISTIC -DCOMMON_PTHREAD -DCOMMON_PTHREAD_BARRIER -DCOMMON_TIMING_OLD', *makefiles)
            if spec.satisfies('+mac'):
                filter_file(r'-lrt', '', *makefiles)

    def install(self, spec, prefix):
        # Currently support gcc and icc on x86_64 (maybe others with
        # vanilla makefile)
        makefile = 'Make.inc/Makefile.inc.x86-64_pc_linux2'
        if spec.satisfies('%icc'):
            makefile += '.icc'

        with working_dir('src'):
            if spec.satisfies('+shared'):
                mf = FileFilter(makefile)
                mf.filter('CFLAGS       =', 'CFLAGS     = -fPIC')

            force_symlink(makefile, 'Makefile.inc')
            for app in ('scotch', 'esmumps'):
                make(app)
            if spec.satisfies('+mpi'):
                make('ptscotch')
                make('ptesmumps',parallel=False)

        install_tree('bin', prefix.bin)
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        install_tree('man/man1', prefix.share_man1)
