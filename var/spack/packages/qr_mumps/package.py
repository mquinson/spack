from spack import *
import os
import spack

class QrMumps(Package):
    """a software package for the solution of sparse, linear systems on multicore computers based on the QR factorization of the input matrix."""
    homepage = "http://buttari.perso.enseeiht.fr/qr_mumps/"

    version('qrm_starpu_2d', svn='https://wwwsecu.irit.fr/svn/qr_mumps/branches/qrm_starpu_2d')

    pkg_dir = spack.db.dirname_for_package_name("qr_mumps")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    depends_on("blas")
    depends_on("lapack")
    depends_on("hwloc")
    depends_on("starpu")
    depends_on("metis@4.0.1:4.0.3")
    depends_on("scotch")
    # for COLAMD
    depends_on("suitesparse")

    def setup(self):
        spec = self.spec
        hwloc = spec['hwloc'].prefix
        starpu = spec['starpu'].prefix
        metis = spec['metis'].prefix
        scotch = spec['scotch'].prefix
        suitesparse = spec['suitesparse'].prefix

        force_symlink('makeincs/Make.inc.gnu', 'Make.inc')
        mf = FileFilter('Make.inc')

        mf.filter('TOPDIR=/path/to/here', 'TOPDIR=%s/qrm_starpu_2d/' % self.stage.path)

        includelist='-I%s' %  metis.include
        includelist+=' -I%s' %  suitesparse.include
        includelist+=' -I%s' %  hwloc.include
        os.environ["PKG_CONFIG_PATH"] = "%s/pkgconfig:$PKG_CONFIG_PATH" % starpu.lib
        includelist+=' `pkg-config --cflags libstarpu`'
        mf.filter('CINCLUDES= \$\(IMETIS\) \$\(ICOLAMD\) \$\(ISTARPU\) \$\(IHWLOC\)', 'CINCLUDES= %s' % includelist)
        mf.filter('FINCLUDES= \$\(ISCOTCH\)', 'FINCLUDES= -I%s' % scotch.include)

        optf = 'FCFLAGS  = -O3 -fPIC'
        optc = 'CFLAGS   = -O3 -fPIC'

        blas_libs = " ".join(blaslibfortname)
        lapack_libs = " ".join(lapacklibfortname)
        mf.filter('LBLAS    = -L/path/to/blas -lblas', 'LBLAS    = %s' % blas_libs)
        mf.filter('LLAPACK  = -L/path/to/lapack -llapack', 'LLAPACK  = %s' % lapack_libs)

        if '^mkl-blas' in spec or '^mkl-lapack' in spec:
            optf+= ' -m64 -I${MKLROOT}/include'
            optc+= ' -m64 -I${MKLROOT}/include'

        mf.filter('FCFLAGS  = -O3', '%s' % optf)
        mf.filter('CFLAGS   = -O3', '%s' % optc)

        mf.filter('LSTARPU = -L/path/to/starpu/lib -lstarpu', 'LSTARPU = `pkg-config --libs libstarpu`')
        mf.filter('ISTARPU = -I/path/to/starpu/include', 'ISTARPU = `pkg-config --cflags libstarpu`')
        mf.filter('# LCOLAMD  = -L/path/to/colamd/Lib -lcolamd', 'LCOLAMD  = -L%s -lcolamd -lsuitesparseconfig' % suitesparse.lib)
        mf.filter('# ICOLAMD  = -I/path/to/colamd/Include -I/path/to/ufconfig', 'ICOLAMD  = -I%s' % suitesparse.include)
        mf.filter('# LMETIS   = -L/path/to/metis -lmetis', 'LMETIS   = -L%s -lmetis' % metis.lib)
        mf.filter('# IMETIS   = -I/path/to/metis/include', 'IMETIS   = -I%s' % metis.include)
        mf.filter('# LSCOTCH  = -L/path/to/scotch/lib -lscotch -lscotcherr', 'LSCOTCH  = -L%s -lscotch -lscotcherr -lpthread' % scotch.lib)
        mf.filter('# ISCOTCH  = -I/path/to/scotch/include', 'ISCOTCH  = -I%s' % scotch.include)
        mf.filter('LHWLOC = -L/path/to/hwloc/lib -lhwloc', 'LHWLOC = -L%s -lhwloc' % hwloc.lib)
        mf.filter('IHWLOC = -I/path/to/hwloc/include', 'IHWLOC = -I%s' % hwloc.include)

        mf = FileFilter('test/Makefile')
        mf.filter('\$\(LSCOTCH\)', '$(LSCOTCH) $(LSTARPU) $(LHWLOC)')

        mf = FileFilter('src/factorization/qrm_factorization_core.F90')
        mf.filter('nworker_per_cuda = starpu_nworker_per_cuda\(\)', '!nworker_per_cuda = starpu_nworker_per_cuda()')
        mf.filter('write\(\*,\'\(\"  Number of workers per CUDA: \",i3\)\'\) nworker_per_cuda', '!write(*,\'(\"  Number of workers per CUDA: \",i3)\') nworker_per_cuda')

    def install(self, spec, prefix):

        self.setup()

        make('dprec', parallel=False)
        #for app in ('sdcz'):
        #    make('%sprec'%app, parallel=False)

        make('dtest', parallel=False)
        #for app in ('sdcz'):
        #    make('%stest'%app, parallel=False)

        with working_dir('examples'):
            make('qrm_test', 'PREC=-Ddprec', 'ARITH=d', parallel=False)

        # No install provided
        install_tree('lib', prefix.lib)
        mkdirp(prefix.include)
        with working_dir('include'):
            for file in os.listdir("%s/qrm_starpu_2d/include" % self.stage.path):
                if file.endswith(".h"):
                    install(file, prefix.include)

        mkdirp('%s/lib/qr_mumps/test' % prefix)
        with working_dir('test'):
            install('dqrm_coverage', '%s/lib/qr_mumps/test' % prefix)
            for file in os.listdir("%s/qrm_starpu_2d/test" % self.stage.path):
                if file.endswith(".txt"):
                    install(file, '%s/lib/qr_mumps/test' % prefix)
                if file.endswith(".mtx"):
                    install(file, '%s/lib/qr_mumps/test' % prefix)

        mkdirp('%s/lib/qr_mumps/examples' % prefix)
        with working_dir('examples'):
            install('dqrm_test', '%s/lib/qr_mumps/examples' % prefix)

    # to use the existing version available in the environment: QR_MUMPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('QR_MUMPS_DIR'):
            qrmumpsroot=os.environ['QR_MUMPS_DIR']
            if os.path.isdir(qrmumpsroot):
                os.symlink(qrmumpsroot+"/bin", prefix.bin)
                os.symlink(qrmumpsroot+"/include", prefix.include)
                os.symlink(qrmumpsroot+"/lib", prefix.lib)
            else:
                sys.exit(qrmumpsroot+' directory does not exist.'+' Do you really have openmpi installed in '+qrmumpsroot+' ?')
        else:
            sys.exit('QR_MUMPS_DIR is not set, you must set this environment variable to the installation path of your qr_mumps')
