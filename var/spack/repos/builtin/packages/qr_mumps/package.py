from spack import *
import os
import platform
import spack
from shutil import copyfile

class QrMumps(Package):
    """a software package for the solution of sparse, linear systems on multicore computers based on the QR factorization of the input matrix."""
    homepage = "http://buttari.perso.enseeiht.fr/qr_mumps/"

    version('trunk', svn='https://wwwsecu.irit.fr/svn/qr_mumps/trunk')
    version('2.0', 'e880670f4dddba16032f43faa03aa903',
            url="http://buttari.perso.enseeiht.fr/qr_mumps/releases/qr_mumps-2.0.tgz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('debug', default=False, description='Enable debug symbols')
    variant('colamd', default=True, description='Enable COLAMD ordering')
    variant('metis', default=False, description='Enable Metis ordering')
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
    depends_on("colamd", when='+colamd')
    depends_on("starpu", when='+starpu')
    depends_on("fxt", when='+fxt')
    depends_on("starpu+fxt", when='+fxt')

    # Don't build correctly in parallel
    parallel = False

    def setup(self):
        spec = self.spec

        if spec.satisfies('+metis') and spec.satisfies('+scotch'):
            raise RuntimeError('You cannot use Metis and Scotch at the same'
             ' time because they are incompatible (Scotch provides a metis.h'
             ' which is not the same as the one providen by Metis)')

        if spec.satisfies('@2.0'):
            stagedir=self.stage.path+'/qr_mumps-2.0'
        elif spec.satisfies('@trunk'):
            stagedir=self.stage.path+'/trunk'

        copyfile('makeincs/Make.inc.gnu', 'makeincs/Make.inc.spack')
        mf = FileFilter('makeincs/Make.inc.spack')

        mf.filter('topdir=\$\(HOME\)/path/to/here', 'topdir=%s/' % stagedir)

        mf.filter('^# CC      =.*', 'CC      = cc')
        mf.filter('^# FC      =.*', 'FC      = f90')

        includelist = ''
        definitions = ''
        hwloc = spec['hwloc'].prefix
        includelist += ' `pkg-config --cflags hwloc`'
        if spec.satisfies('+colamd'):
            colamd = spec['colamd'].prefix
            includelist += ' -I%s' %  colamd.include
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
        if spec.satisfies("%xl"):
            optf = 'FCFLAGS  = -O3 -qpic -qhot -qtune=auto -qarch=auto'
            optc = 'CFLAGS   = -O3 -qpic -qhot -qtune=auto -qarch=auto'
            mf.filter('^DEFINE_PREPEND =.*', 'DEFINE_PREPEND = -WF,')
            definitionsWF = definitions.replace('-D', '-WF,-D')
            mf.filter('FDEFS =.*', 'FDEFS = %s' % definitionsWF)
        if spec.satisfies('+debug'):
            optf += ' -g'
            optc += ' -g'
        if '^mkl' in spec:
            optf+= ' -m64 -I${MKLROOT}/include'
            optc+= ' -m64 -I${MKLROOT}/include'
        if spec.satisfies("%intel"):
            # The ifort default runtime is not thread safe. Adding the
            # -qopenmp flag ensures that thread-safe code is generated
            # and a thread-safe runtime is linked
            mf.filter('^LDFLAGS.*', 'LDFLAGS = $(FCFLAGS) -nofor_main -openmp')
            optf = 'FCFLAGS  = -O3 -fPIC -openmp'
            optc = 'CFLAGS   = -O3 -fPIC'
        mf.filter('^FCFLAGS =.*', '%s' % optf)
        mf.filter('^CFLAGS  =.*', '%s' % optc)

        blas_libs = spec['blas'].fc_link
        lapack_libs = spec['lapack'].fc_link
        mf.filter('^LBLAS    =.*', 'LBLAS    = %s' % blas_libs)
        mf.filter('^LLAPACK  =.*', 'LLAPACK  = %s' % lapack_libs)

        if spec.satisfies('+colamd'):
            colamd_libs = spec['colamd'].cc_link
            mf.filter('^# LCOLAMD  =.*', 'LCOLAMD  = %s' % colamd_libs)
            mf.filter('^# ICOLAMD  =.*', 'ICOLAMD  = -I%s' % colamd.include)
        if spec.satisfies('+metis'):
            metis_libs = spec['metis'].cc_link
            mf.filter('^# LMETIS   =.*', 'LMETIS   = %s' % metis_libs)
            mf.filter('^# IMETIS   =.*', 'IMETIS   = -I%s' % metis.include)
        if spec.satisfies('+scotch'):
            scotch_libs = spec['scotch'].cc_link
            mf.filter('^# LSCOTCH  =.*', 'LSCOTCH  = %s' % scotch_libs)
            mf.filter('^# ISCOTCH  =.*', 'ISCOTCH  = -I%s' % scotch.include)
        if spec.satisfies('+starpu'):
            mf.filter('^# LSTARPU =.*', 'LSTARPU = `pkg-config --libs libstarpu`')
            mf.filter('^# ISTARPU =.*', 'ISTARPU = `pkg-config --cflags libstarpu`')


    def install(self, spec, prefix):

        self.setup()

        ariths=["d", "s", "z", "c"]

        if spec.satisfies('@2.0'):
            stagedir=self.stage.path+'/qr_mumps-2.0'
        elif spec.satisfies('@trunk'):
            stagedir=self.stage.path+'/trunk'
        
        make('setup', 'BUILD=build', 'PLAT=spack')
        with working_dir('build'):

            for a in ariths:
                make('lib', 'BUILD=build', 'PLAT=spack', 'ARITH='+a)
                make('examples', 'BUILD=build', 'PLAT=spack', 'ARITH='+a)
                make('testing', 'BUILD=build', 'PLAT=spack', 'ARITH='+a)

            ## No install provided
            # install lib
            install_tree('lib', prefix.lib)
            # install headers
            mkdirp(prefix.include)
            for file in os.listdir("%s/build/include" % stagedir):
                install("include/"+file, prefix.include)
            # install examples
            mkdirp('%s/examples' % prefix)
            for executable in ["qrm_front", "qrm_test"]:
                for a in ariths:
                    install('examples/'+a+executable, '%s/examples/' % prefix)
            # install testing
            mkdirp('%s/testing' % prefix)
            for executable in ["qrm_testing", "qrm_testing"]:
                for a in ariths:
                    install('testing/'+a+executable, '%s/testing/' % prefix)
            pkg_dir = spack.repo.dirname_for_package_name("qr_mumps")
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
                raise RuntimeError(qrmumpsroot+' directory does not exist.'+' Do you really have qr_mumps installed in '+qrmumpsroot+' ?')
        else:
            raise RuntimeError('QR_MUMPS_DIR is not set, you must set this environment variable to the installation path of your qr_mumps')
