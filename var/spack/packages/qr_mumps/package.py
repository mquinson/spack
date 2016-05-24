from spack import *
import os
import platform
import spack
from shutil import copyfile

class QrMumps(Package):
    """a software package for the solution of sparse, linear systems on multicore computers based on the QR factorization of the input matrix."""
    homepage = "http://buttari.perso.enseeiht.fr/qr_mumps/"

    version('trunk', svn='https://wwwsecu.irit.fr/svn/qr_mumps/trunk')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('debug', default=False, description='Enable debug symbols')
    variant('colamd', default=True, description='Enable COLAMD ordering')
    variant('metis', default=True, description='Enable Metis ordering')
    variant('scotch', default=True, description='Enable Scotch ordering')
    variant('starpu', default=True, description='Enable StarPU runtime system support')
    variant('fxt', default=False, description='Enable FxT tracing support to be used through StarPU')

    # dependencies
    depends_on("blas")
    depends_on("lapack")
    depends_on("hwloc")
    # optional dependencies
    depends_on("metis", when='+metis')
    depends_on("scotch", when='+scotch')
    depends_on("suitesparse", when='+colamd') # for COLAMD
    depends_on("starpu", when='+starpu')
    depends_on("fxt", when='+fxt')
    depends_on("starpu+fxt", when='+fxt')

    def setup(self):
        spec = self.spec

        copyfile('makeincs/Make.inc.gnu', 'makeincs/Make.inc.spack')
        mf = FileFilter('makeincs/Make.inc.spack')

        mf.filter('topdir=\$\(HOME\)/path/to/here', 'topdir=%s/trunk/' % self.stage.path)

        mf.filter('^# CC      =.*', 'CC      = cc')
        mf.filter('^# FC      =.*', 'FC      = f90')

        includelist = ''
        definitions = ''
        hwloc = spec['hwloc'].prefix
        includelist += ' `pkg-config --cflags hwloc`'
        if spec.satisfies('+colamd'):
            suitesparse = spec['suitesparse'].prefix
            includelist += ' -I%s' %  suitesparse.include
            definitions += ' -Dhave_colamd'
        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            includelist += ' -I%s' %  metis.include
            definitions += ' -Dhave_metis'
        if spec.satisfies('+scotch'):
            scotch = spec['scotch'].prefix
            mf.filter('FINCLUDES=.*', 'FINCLUDES= -I%s' % scotch.include)
            definitions += ' -Dhave_scotch'
        if spec.satisfies('+starpu'):
            starpu = spec['starpu'].prefix
            includelist += ' `pkg-config --cflags libstarpu`'
            definitions += ' -Dhave_starpu'
        if spec.satisfies('+fxt'):
            definitions += ' -Dhave_fxt'
        mf.filter('CINCLUDES=.*', 'CINCLUDES= %s' % includelist)
        mf.filter('CDEFS =.*', 'CDEFS = %s' % definitions)
        mf.filter('FDEFS =.*', 'FDEFS = %s' % definitions)

        optf = 'FCFLAGS  = -O3 -fPIC'
        optc = 'CFLAGS   = -O3 -fPIC'
        if spec.satisfies('+debug'):
            optf += ' -g'
            optc += ' -g'
        if '^mkl-blas' in spec or '^mkl-lapack' in spec:
            optf+= ' -m64 -I${MKLROOT}/include'
            optc+= ' -m64 -I${MKLROOT}/include'
        mf.filter('^FCFLAGS =.*', '%s' % optf)
        mf.filter('^CFLAGS  =.*', '%s' % optc)

        blas_libs = " ".join(blaslibfortname)
        lapack_libs = " ".join(lapacklibfortname)
        mf.filter('^# LBLAS    =.*', 'LBLAS    = %s' % blas_libs)
        mf.filter('^# LLAPACK  =.*', 'LLAPACK  = %s' % lapack_libs)

        mf.filter('^# LHWLOC =.*', 'LHWLOC = -L%s -lhwloc' % hwloc.lib)
        mf.filter('^# IHWLOC =.*', 'IHWLOC = -I%s' % hwloc.include)

        if spec.satisfies('+colamd'):
            mf.filter('^# LCOLAMD  =.*', 'LCOLAMD  = -L%s -lcolamd -lsuitesparseconfig' % suitesparse.lib)
            if platform.system() != 'Darwin':
                mf.filter('-lsuitesparseconfig', '-lsuitesparseconfig -lrt')
            mf.filter('^# ICOLAMD  =.*', 'ICOLAMD  = -I%s' % suitesparse.include)
        if spec.satisfies('+metis'):
            mf.filter('^# LMETIS   =.*', 'LMETIS   = -L%s -lmetis' % metis.lib)
            mf.filter('^# IMETIS   =.*', 'IMETIS   = -I%s' % metis.include)
        if spec.satisfies('+scotch'):
            mf.filter('^# LSCOTCH  =.*', 'LSCOTCH  = -L%s -lscotch -lscotcherr -lpthread' % scotch.lib)
            mf.filter('^# ISCOTCH  =.*', 'ISCOTCH  = -I%s' % scotch.include)
        if spec.satisfies('+starpu'):
            mf.filter('^# LSTARPU =.*', 'LSTARPU = `pkg-config --libs libstarpu`')
            mf.filter('^# ISTARPU =.*', 'ISTARPU = `pkg-config --cflags libstarpu`')


    def install(self, spec, prefix):

        self.setup()

        make('setup', 'BUILD=build', 'PLAT=spack', 'ARITH=d s', parallel=False)
        with working_dir('build'):
            make('lib', 'BUILD=build', 'PLAT=spack', 'ARITH=d s', parallel=False)
            make('examples', 'BUILD=build', 'PLAT=spack', 'ARITH=d s', parallel=False)
            make('testing', 'BUILD=build', 'PLAT=spack', 'ARITH=d s', parallel=False)

            ## No install provided
            # install lib
            install_tree('lib', prefix.lib)
            # install headers
            mkdirp(prefix.include)
            for file in os.listdir("%s/trunk/build/include" % self.stage.path):
                install("include/"+file, prefix.include)
            # install examples
            mkdirp('%s/examples' % prefix)
            for executable in ["dqrm_front", "dqrm_test", "sqrm_front", "sqrm_test"]:
                install('examples/'+executable, '%s/examples/' % prefix)
            # install testing
            mkdirp('%s/testing' % prefix)
            for executable in ["dqrm_testing", "sqrm_testing"]:
                install('testing/'+executable, '%s/testing/' % prefix)
            pkg_dir = spack.db.dirname_for_package_name("qr_mumps")
            install(pkg_dir+'/matfile.txt', '%s/testing/' % prefix)
            install(pkg_dir+'/cage5.mtx', '%s/testing/' % prefix)


    # to use the existing version available in the environment: QR_MUMPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('QR_MUMPS_DIR'):
            qrmumpsroot=os.environ['QR_MUMPS_DIR']
            if os.path.isdir(qrmumpsroot):
                os.symlink(qrmumpsroot+"/examples", prefix.bin)
                os.symlink(qrmumpsroot+"/include", prefix.include)
                os.symlink(qrmumpsroot+"/lib", prefix.lib)
            else:
                sys.exit(qrmumpsroot+' directory does not exist.'+' Do you really have openmpi installed in '+qrmumpsroot+' ?')
        else:
            sys.exit('QR_MUMPS_DIR is not set, you must set this environment variable to the installation path of your qr_mumps')
