from spack import *
import os
import platform
import spack
import sys

class Mumps(Package):
    """a MUltifrontal Massively Parallel sparse direct Solver."""
    homepage = "http://mumps.enseeiht.fr/"

    version('4.10.0', '959e9981b606cd574f713b8422ef0d9f',
            url="http://mumps.enseeiht.fr/MUMPS_4.10.0.tar.gz")
    version('5.0.0', '3c6aeab847e9d775ca160194a9db2b75',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.0.tar.gz")
    version('5.0.1', 'b477573fdcc87babe861f62316833db0',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.1.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("mumps")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    variant('seq', default=False, description='Sequential version (no MPI)')
    variant('scotch', default=False, description='Enable Scotch')
    variant('ptscotch', default=False, description='Enable PT-Scotch')
    variant('metis', default=False, description='Enable Metis')
    variant('shared', default=True, description='Build MUMPS as a shared library')
    variant('examples', default=False, description='Enable compilation and installation of example executables')

    depends_on("mpi", when='~seq')
    depends_on("blas")
    depends_on("scalapack")
    depends_on("scotch", when='+scotch')
    depends_on("scotch+mpi", when='+ptscotch')
    depends_on("metis@5:", when='@5:+metis')
    depends_on("metis@:4", when='@:4+metis')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for Mumps."""
        libdir = self.spec.prefix.lib
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
        else:
            libext=".a"

        module.mumpslibname = []
        for l in ["smumps", "dmumps", "cmumps", "zmumps", "mumps_common", "pord"]:
            module.mumpslibname  += [os.path.join(libdir, "lib%s%s"%(l, libext))]

        # there is a bug with the hash calculation of mumps
        module.mumpsprefix=self.spec.prefix

    def setup(self):
        spec = self.spec
        if spec.satisfies('~seq@5'):
            force_symlink('Make.inc/Makefile.debian.PAR', 'Makefile.inc')
        if spec.satisfies('+seq@5'):
            force_symlink('Make.inc/Makefile.debian.SEQ', 'Makefile.inc')
        if spec.satisfies('~seq@4'):
            force_symlink('Make.inc/Makefile.inc.generic', 'Makefile.inc')
        if spec.satisfies('+seq@4'):
            force_symlink('Make.inc/Makefile.inc.generic.SEQ', 'Makefile.inc')

        mf = FileFilter('Makefile.inc')

        ordlist='-Dpord'

        if spec.satisfies('+scotch'):
            scotch = spec['scotch'].prefix
            mf.filter('.*LSCOTCHDIR\s*=.*', 'LSCOTCHDIR = %s' % scotch.lib)
            mf.filter('.*SCOTCHDIR\s*=.*', 'SCOTCHDIR = %s' % scotch.lib)
            mf.filter('.*ISCOTCH\s*=.*', 'ISCOTCH = -I%s' % scotch.include)
            mf.filter('.*LSCOTCH\s*=.*', 'LSCOTCH   = '+" ".join(scotchlibname))
            ordlist+=' -Dscotch'

        if spec.satisfies('+ptscotch'):
            scotch = spec['scotch'].prefix
            mf.filter('LSCOTCH\s*=.*', 'LSCOTCH   = -L$(LSCOTCHDIR) -lptesmumps -lptscotch -lptscotcherr -lesmumps -lscotch -lscotcherr')
            mf.filter('^#ISCOTCH\s*=.*', 'ISCOTCH = -I%s' % scotch.include)
            ordlist+=' -Dptscotch'

        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            mf.filter('.*LMETISDIR\s*=.*', 'LMETISDIR = %s' % metis.lib)
            mf.filter('.*IMETIS\s*=.*', 'IMETIS    = -I%s' % metis.include)
            mf.filter('.*LMETIS\s*=.*', 'LMETIS = ' + " ".join(metislibname))
            ordlist+=' -Dmetis'

        if spec.satisfies('+parmetis'):
            parmetis = spec['parmetis'].prefix
            mf.filter('^LMETISDIR\s*=.*', 'LMETISDIR = %s' % parmetis.lib)
            mf.filter('^IMETIS\s*=.*', 'IMETIS = -I%s' % parmetis.include)
            mf.filter('^LMETIS\s*=.*', 'LMETIS = -L$(LMETISDIR) -lparmetis')
            ordlist+=' -Dparmetis'

        mf.filter('^ORDERINGSF\s*=.*', 'ORDERINGSF = %s' % ordlist)

        if spec.satisfies('~scotch') and spec.satisfies('~ptscotch') :
            mf.filter('^LSCOTCH\s*=.*', '#LSCOTCH   =')

        if spec.satisfies('~metis'):
            mf.filter('^IMETIS\s*=.*', '#IMETIS    =')
            mf.filter('^LMETIS\s*=.*', '#LMETIS    =')

        blas_libs = " ".join(blaslibname)
        lapack_libs = " ".join(lapacklibname)
        try:
            blacs_libs = " ".join(blacslibname)
        except NameError:
            blacs_libs = ''
        scalapack_libs = " ".join(scalapacklibname)
        mf.filter('^SCALAP  =.*', 'SCALAP  = '+scalapack_libs+' '+blacs_libs+' '+lapack_libs+' '+blas_libs)
        mf.filter('^LIBBLAS =.*', 'LIBBLAS = %s' % blas_libs)

        if '^mkl-scalapack' in spec:
            mf.filter('^OPTF\s*=.*', 'OPTF = -O  -DALLOW_NON_INIT -fPIC -m64 -I${MKLROOT}/include')
        else:
            mf.filter('^OPTF\s*=.*', 'OPTF = -O  -DALLOW_NON_INIT -fPIC')
        mf.filter('^OPTC\s*=.*', 'OPTC    = -O -fPIC')

        if spec.satisfies("%intel"):
            mf.filter('^OPTL\s*=', 'OPTL = -nofor-main ')

        mpi = spec['mpi'].prefix
        if spec.satisfies("%intel") and 'intelmpi' in self.spec['mpi']:
            mpicc = "mpiicc"
            mpif90 = "mpiifort"
        else:
            mpicc = binmpicc
            mpif90 = binmpif90
        mf.filter('CC\s*=.*', 'CC = %s' % mpicc)
        mf.filter('FC\s*=.*', 'FC = %s' % mpif90)
        mf.filter('FL\s*=.*', 'FL = %s' % mpif90)
        mf.filter('^INCPAR.*', 'INCPAR = -I%s' % mpi.include)
        mf.filter('^LIBPAR.*', 'LIBPAR = $(SCALAP)')

        mf.filter('^LIBOTHERS =.*', 'LIBOTHERS = -lz -lm -lrt -lpthread')

        if spec.satisfies('+shared'):
            mf.filter('^AR\s*=.*', 'AR=$(FC) $(SCALAP) $(LSCOTCH) $(LMETIS) -shared -o ')
            mf.filter('^RANLIB\s*=.*', 'RANLIB=echo ')
            if platform.system() == 'Darwin':
                mf.filter('-shared -o', '-shared -undefined dynamic_lookup -o')
                mf.filter('^LIBEXT\s*=.*', 'LIBEXT = .dylib')
            else:
                mf.filter('^LIBEXT\s*=.*', 'LIBEXT = .so')

        if platform.system() == 'Darwin':
            mf.filter('-lrt', '');

    def install(self, spec, prefix):

        self.setup()

        for app in ('s', 'd', 'c', 'z'):
            make(app)

        if spec.satisfies('+examples'):
            for app in ('sexamples', 'dexamples', 'cexamples', 'zexamples'):
                make(app)

        # No install provided
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        if spec.satisfies('+seq~shared'):
            install('libseq/libmpiseq.a', prefix.lib)
        if spec.satisfies('+seq+shared'):
            if platform.system() == 'Darwin':
                install('libseq/libmpiseq.dylib', prefix.lib)
            else:
                install('libseq/libmpiseq.so', prefix.lib)
        if spec.satisfies('+examples'):
            install_tree('examples', '%s/lib/mumps/examples' % prefix)

    # to use the existing version available in the environment: MUMPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('MUMPS_DIR'):
            mumpsroot=os.environ['MUMPS_DIR']
            if os.path.isdir(mumpsroot):
                os.symlink(mumpsroot+"/bin", prefix.bin)
                os.symlink(mumpsroot+"/include", prefix.include)
                os.symlink(mumpsroot+"/lib", prefix.lib)
            else:
                sys.exit(mumpsroot+' directory does not exist.'+' Do you really have openmpi installed in '+mumpsroot+' ?')
        else:
            sys.exit('MUMPS_DIR is not set, you must set this environment variable to the installation path of your mumps')
