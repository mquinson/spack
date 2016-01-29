from spack import *
import os
import platform
import sys
import spack

class Hips(Package):
    """Hierarchical Iterative Parallel Solver."""
    homepage = "http://hips.gforge.inria.fr/index.html"

    version('1.2b-rc5', '385f66475eb77e3dce27c6a9a53232e8',
            url='http://hips.gforge.inria.fr/release/hips-1.2b-rc5.tar.gz')

    variant('complex',  default=False, description='Build complex float version (real by default)')
    variant('simple',   default=False, description='Build simple precision version (double by default)')
    variant('metis',    default=False, description='Use Metis partitioner')
    variant('shared',   default=False,  description='Build Hips as a shared library')
    variant('int64',    default=False, description='To use 64 bits integers')
    variant('examples', default=True,  description='Enable compilation and installation of example executables')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on("mpi")
    depends_on("metis@:4", when='+metis')
    depends_on("scotch",   when='~metis')
    depends_on("blas")

    def setup(self):
        force_symlink('Makefile_Inc_Examples/makefile.inc.gnu', 'makefile.inc')

        mf = FileFilter('makefile.inc')
        spec = self.spec

        if spec.satisfies('+complex'):
            if spec.satisfies('+simple'):
                mf.filter('^COEFTYPE     =.*', 'COEFTYPE     = -DTYPE_COMPLEX -DPREC_SIMPLE')
            else:
                mf.filter('^COEFTYPE     =.*', 'COEFTYPE     = -DTYPE_COMPLEX -DPREC_DOUBLE')
        else:
            if spec.satisfies('+simple'):
                mf.filter('^COEFTYPE     =*.', 'COEFTYPE     = -DTYPE_REAL    -DPREC_SIMPLE')
            else:
                mf.filter('^COEFTYPE     =.*', 'COEFTYPE     = -DTYPE_REAL    -DPREC_DOUBLE')

        mf.filter('= gcc', '= cc')
        mf.filter('= gfortran', '= f90')

        blas = spec['blas'].prefix
        blas_libs = " ".join(blaslibname)
        mf.filter('^LBLAS      =.*', 'LBLAS      = %s' % blas_libs)

        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            metis_libs = " ".join(metislibname)
            mf.filter('^METIS_DIR  =.*', 'METIS_DIR  = %s' % metis)
            mf.filter('^IMETIS     =.*', 'IMETIS     = %s' % metis.include)
            mf.filter('^LMETIS     =.*', 'LMETIS     = %s' % metis_libs)
            mf.filter('^SCOTCH_DIR =.*', '#SCOTCH_DIR =')
            mf.filter('^ISCOTCH    =.*', '#ISCOTCH    =')
            mf.filter('^LSCOTCH    =.*', '#LSCOTCH    =')
        else:
            mf.filter('^PARTITIONER  =.*', 'PARTITIONER  = -DSCOTCH_PART')
            mf.filter('^METIS_DIR  =.*', '#METIS_DIR  =')
            mf.filter('^IMETIS     =.*', '#IMETIS     =')
            mf.filter('^LMETIS     =.*', '#LMETIS     =')
            scotch = spec['scotch'].prefix
            scotch_libs = " ".join(scotchlibname)
            mf.filter('^SCOTCH_DIR =.*', 'SCOTCH_DIR = %s' % scotch)
            mf.filter('^ISCOTCH    =.*', 'ISCOTCH    = -I%s' % scotch.include)
            mf.filter('^LSCOTCH    =.*', 'LSCOTCH    = %s' % scotch_libs)

        if spec.satisfies('+int64'):
            mf.filter('^INTSIZE      =.*', 'INTSIZE      = -DINTSIZE64')

        if spec.satisfies('+shared'):
            mf.filter('= ar', '= cc')
            mf.filter('^ARFLAGS.*', 'ARFLAGS    = -shared -o\nRANLIB     = echo\nLIB        = .so\nOBJ        = .o')
            sys.exit('Dynamic libs not supported for now. Please use ~shared variant.')

    def install(self, spec, prefix):

        self.setup()
        make()
        if spec.satisfies('+examples'):
            make('all')
        # No install provided
        install_tree('LIB', prefix.lib)
        if spec.satisfies('+examples'):
            install_tree('TESTS', '%s/examples' % prefix)

    # to use the existing version available in the environment: HIPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('HIPS_DIR'):
            hipsroot=os.environ['HIPS_DIR']
            if os.path.isdir(hipsroot):
                os.symlink(hipsroot+"/lib", prefix.lib)
            else:
                sys.exit(hipsroot+' directory does not exist.'+' Do you really have openmpi installed in '+hipsroot+' ?')
        else:
            sys.exit('HIPS_DIR is not set, you must set this environment variable to the installation path of your hips')
