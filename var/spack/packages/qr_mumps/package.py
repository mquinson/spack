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
    variant('fxt', default=False, description='Enable FxT tracing support')

    depends_on("blas")
    depends_on("lapack")
    depends_on("hwloc")
    depends_on("starpu")
    depends_on("metis@4.0.1:4.0.3")
    depends_on("scotch")
    # for COLAMD
    depends_on("suitesparse")
    depends_on("fxt", when='+fxt')
    depends_on("starpu+fxt", when='+fxt')

    def setup(self):
        spec = self.spec
        hwloc = spec['hwloc'].prefix
        starpu = spec['starpu'].prefix
        metis = spec['metis'].prefix
        scotch = spec['scotch'].prefix
        suitesparse = spec['suitesparse'].prefix

        copyfile('makeincs/Make.inc.gnu', 'makeincs/Make.inc.spack')
        mf = FileFilter('makeincs/Make.inc.spack')

        mf.filter('topdir=\$\(HOME\)/path/to/here', 'topdir=%s/trunk/' % self.stage.path)

        mf.filter('CC      = gcc', 'CC      = cc')
        mf.filter('FC      = gfortran', 'FC      = f90')

        includelist='-I%s' %  metis.include
        includelist+=' -I%s' %  suitesparse.include
        includelist+=' `pkg-config --cflags hwloc`'
        includelist+=' `pkg-config --cflags libstarpu`'
        mf.filter('CINCLUDES=.*', 'CINCLUDES= %s' % includelist)
        mf.filter('FINCLUDES=.*', 'FINCLUDES= -I%s' % scotch.include)

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
        mf.filter('^# LSTARPU =.*', 'LSTARPU = `pkg-config --libs libstarpu`')
        mf.filter('^# ISTARPU =.*', 'ISTARPU = `pkg-config --cflags libstarpu`')
        mf.filter('^# LCOLAMD  =.*', 'LCOLAMD  = -L%s -lcolamd -lsuitesparseconfig' % suitesparse.lib)
        if platform.system() != 'Darwin':
            mf.filter('-lsuitesparseconfig', '-lsuitesparseconfig -lrt')
        mf.filter('^# ICOLAMD  =.*', 'ICOLAMD  = -I%s' % suitesparse.include)
        mf.filter('^# LMETIS   =.*', 'LMETIS   = -L%s -lmetis' % metis.lib)
        mf.filter('^# IMETIS   =.*', 'IMETIS   = -I%s' % metis.include)
        mf.filter('^# LSCOTCH  =.*', 'LSCOTCH  = -L%s -lscotch -lscotcherr -lpthread' % scotch.lib)
        mf.filter('^# ISCOTCH  =.*', 'ISCOTCH  = -I%s' % scotch.include)
        mf.filter('^# LHWLOC =.*', 'LHWLOC = -L%s -lhwloc' % hwloc.lib)
        mf.filter('^# IHWLOC =.*', 'IHWLOC = -I%s' % hwloc.include)

        if not spec.satisfies('+fxt'):
            mf.filter('-Dhave_fxt', '')


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
