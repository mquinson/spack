from spack import *
import glob
import os
from subprocess import call

class ScotchEsmumps(Package):
    """Scotch is a software package for graph and mesh/hypergraph
       partitioning, graph clustering, and sparse matrix ordering."""
    homepage = "http://www.labri.fr/perso/pelegrin/scotch/"
    url      = "https://gforge.inria.fr/frs/download.php/file/31832/scotch_6.0.0_esmumps.tar.gz"

    version('6.0.0', 'c50d6187462ba801f9a82133ee666e8e')

    depends_on('mpi')


    def patch(self):
        with working_dir('src/Make.inc'):
            spec = self.spec
            makefiles = glob.glob('Makefile.inc.x86-64_pc_linux2*')
            filter_file(r'^CCS\s*=.*$', 'CCS = cc', *makefiles)
            filter_file(r'^CCD\s*=.*$', 'CCD = cc', *makefiles)
            filter_file(r'-O3 -DCOMMON_FILE_COMPRESS_GZ', '-O3 -pthread -DCOMMON_FILE_COMPRESS_GZ', *makefiles)
            if spec.satisfies('%icc'):
                call(["cp", "Makefile.inc.x86-64_pc_linux2.shlib", "Makefile.inc.x86-64_pc_linux2.shlib.icc"])
                filter_file(r'^CLIBFLAGS\s*=.*$', 'CLIBFLAGS = -shared -fpic', *makefiles)

        with working_dir('src/esmumps'):
            mf = FileFilter('Makefile')
            mf.filter('\$\(CC\) \$\(CFLAGS\) -I\$\(includedir\).*', '$(CC) $(CFLAGS) -I$(includedir) $(<) -o $(@) -L$(libdir) $(LDFLAGS) -L. -l$(ESMUMPSLIB) -l$(SCOTCHLIB) -lscotch -l$(SCOTCHLIB)errexit -lz -lm')


    def install(self, spec, prefix):
        # Currently support gcc and icc on x86_64 (maybe others with
        # vanilla makefile)
        makefile = 'Make.inc/Makefile.inc.x86-64_pc_linux2.shlib'
        if spec.satisfies('%icc'):
            makefile += '.icc'

        with working_dir('src'):
            force_symlink(makefile, 'Makefile.inc')
            for app in ('scotch', 'ptscotch','esmumps'):
                make(app)
            make('ptesmumps',parallel=False)

        install_tree('bin', prefix.bin)
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        install_tree('man/man1', prefix.share_man1)
