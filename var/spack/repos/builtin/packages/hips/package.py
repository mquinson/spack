from spack import *
import os
import platform
import sys
import spack
from shutil import copyfile
import subprocess

class Hips(Package):
    """Hierarchical Iterative Parallel Solver."""
    homepage = "http://hips.gforge.inria.fr/index.html"

    version('1.2b-rc5', '385f66475eb77e3dce27c6a9a53232e8',
            url='http://hips.gforge.inria.fr/release/hips-1.2b-rc5.tar.gz')
    version('trunk', svn='https://scm.gforge.inria.fr/anonscm/svn/hips/trunk')

    variant('complex',  default=False, description='Build complex float version (real by default)')
    variant('simple',   default=False, description='Build simple precision version (double by default)')
    variant('metis',    default=False, description='Use Metis partitioner')
    variant('pastix',   default=False, description='Enable PASTIX direct solver, only available with the trunk version of hips')
    variant('idx64',    default=False, description='To use 64 bits integers')
    variant('shared',   default=False,  description='Build Hips as a shared library')
    variant('examples', default=True,  description='Enable compilation and installation of example executables')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on("mpi")
    depends_on("metis@:4", when='+metis')
    depends_on("scotch", when='~metis')
    depends_on("scotch+idx64", when='~metis+idx64')
    depends_on("blas")
    depends_on("pastix", when='@trunk+pastix')

    def setup(self):
        copyfile('Makefile_Inc_Examples/makefile.inc.gnu', 'makefile.inc')

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

        mpi = spec['mpi'].prefix
        try:
            mpicc = spec['mpi'].mpicc
        except AttributeError:
            mpicc = 'mpicc'
        try:
            mpif90 = spec['mpi'].mpifc
        except AttributeError:
            mpif90 = 'mpif90'
        mf.filter('= gcc', '= cc')
        mf.filter('= gfortran', '= f90')
        mf.filter('= mpicc', '= %s' % mpicc)
        mf.filter('= mpif90', '= %s' % mpif90)

        blas = spec['blas'].prefix
        blas_libs = spec['blas'].cc_link
        mf.filter('^LBLAS      =.*', 'LBLAS      = %s' % blas_libs)

        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            metis_libs = spec['metis'].cc_link
            mf.filter('^METIS_DIR  =.*', 'METIS_DIR  = %s' % metis)
            mf.filter('^IMETIS     =.*', 'IMETIS     = -I%s' % metis.include)
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
            scotch_libs = spec['scotch'].cc_link
            mf.filter('^SCOTCH_DIR =.*', 'SCOTCH_DIR = %s' % scotch)
            mf.filter('^ISCOTCH    =.*', 'ISCOTCH    = -I%s' % scotch.include)
            mf.filter('^LSCOTCH    =.*', 'LSCOTCH    = %s' % scotch_libs)

        if spec.satisfies('+pastix'):
            if not spec.satisfies('@trunk'):
                raise RuntimeError('Only the trunk version of Hips support PaStiX for now, please use hips@trunk.')
            pastix = spec['pastix'].prefix
            pastix_libs = subprocess.Popen([pastix+"/bin/pastix-conf", "--libs"], stdout=subprocess.PIPE).communicate()[0]
            mf.filter('^PASTIX_DIR =.*', 'PASTIX_DIR = %s' % pastix)
            mf.filter('^IPASTIX =.*', 'IPASTIX = -DWITH_PASTIX -I%s' % pastix.include)
            mf.filter('^LPASTIX =.*', 'LPASTIX = %s' % pastix_libs)
        else:
            mf.filter('^PASTIX_DIR =.*', '#PASTIX_DIR =')
            mf.filter('^IPASTIX =.*', '#IPASTIX =')
            mf.filter('^LPASTIX =.*', '#LPASTIX =')

        if spec.satisfies('+idx64'):
            mf.filter('^INTSIZE      =.*', 'INTSIZE      = -DINTSIZE64')

        if spec.satisfies('+shared'):
            mf.filter('= ar', '= cc')
            mf.filter('^ARFLAGS.*', 'ARFLAGS    = -shared -o\nRANLIB     = echo\nLIB        = .so\nOBJ        = .o')
            raise RuntimeError('Dynamic libs not supported for now. Please use ~shared variant.')

    def install(self, spec, prefix):

        self.setup()
        make()
        if spec.satisfies('+examples'):
            make('all', '-i')
        # No install provided
        install_tree('LIB', prefix.lib)
        if spec.satisfies('+examples'):
            # only the following subdirectories should be copied
            # because make is not done in others with the "all" target
            install_tree('TESTS/PARALLEL',       '%s/TESTS/PARALLEL' % prefix)
            install_tree('TESTS/MATRICES',       '%s/TESTS/MATRICES' % prefix)
            if spec.satisfies('@trunk'):
                install_tree('TESTS/DBMATRIX',       '%s/TESTS/DBMATRIX' % prefix)
                install_tree('TESTS/SEQUENTIAL',     '%s/TESTS/SEQUENTIAL' % prefix)
                install_tree('TESTS/MISC_PARALLEL',  '%s/TESTS/MISC_PARALLEL' % prefix)

    # to use the existing version available in the environment: HIPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('HIPS_DIR'):
            hipsroot=os.environ['HIPS_DIR']
            if os.path.isdir(hipsroot):
                os.symlink(hipsroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(hipsroot+' directory does not exist.'+' Do you really have openmpi installed in '+hipsroot+' ?')
        else:
            raise RuntimeError('HIPS_DIR is not set, you must set this environment variable to the installation path of your hips')
