from spack import *
import os
import platform
import spack
import sys
from shutil import copyfile

class Mumps(Package):
    """a MUltifrontal Massively Parallel sparse direct Solver."""
    homepage = "http://mumps.enseeiht.fr/"

    version('4.10.0', '959e9981b606cd574f713b8422ef0d9f',
            url="http://mumps.enseeiht.fr/MUMPS_4.10.0.tar.gz")
    version('5.0.0', '3c6aeab847e9d775ca160194a9db2b75',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.0.tar.gz")
    version('5.0.1', 'b477573fdcc87babe861f62316833db0',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.1.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('blasmt', default=False, description='Enable Multithreaded Blas/Lapack if providen by the vendor')
    variant('mpi', default=True, description='Sequential version (no MPI)')
    variant('scotch', default=True, description='Enable Scotch')
    variant('ptscotch', default=False, description='Enable PT-Scotch')
    variant('metis', default=True, description='Enable Metis')
    variant('shared', default=True, description='Build MUMPS as a shared library')
    variant('examples', default=True, description='Enable compilation and installation of example executables')

    depends_on("mpi", when='+mpi')
    depends_on("blas")
    depends_on("lapack")
    depends_on("scalapack", when='+mpi')
    depends_on("scotch+esmumps", when='+scotch')
    depends_on("scotch+esmumps+mpi", when='+ptscotch')
    depends_on("metis@5:", when='@src+metis')
    depends_on("metis@5:", when='@5:+metis')
    depends_on("metis@:4", when='@4+metis')

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

        if spec.satisfies('~mpi'):
            # mumps libmpiseq provides dummy symbols for MPI and ScaLAPACK
            # be aware that it must come after the actual MPI library during the link phase
            module.mumpslibname  += [os.path.join(libdir, "libmpiseq%s" % libext)]

        # there is a bug with the hash calculation of mumps
        module.mumpsprefix=self.spec.prefix

    def setup(self):
        spec = self.spec
        if spec.satisfies('+mpi'):
            if spec.satisfies('@4'):
                copyfile('Make.inc/Makefile.inc.generic', 'Makefile.inc')
            else:
                # @5
                copyfile('Make.inc/Makefile.debian.PAR', 'Makefile.inc')
        else:
            # ~mpi
            if spec.satisfies('@4'):
                copyfile('Make.inc/Makefile.inc.generic.SEQ', 'Makefile.inc')
            else:
                # @5
                copyfile('Make.inc/Makefile.debian.SEQ', 'Makefile.inc')

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


        if spec.satisfies('+blasmt'):
            if 'parblaslibname' in globals():
                blas_libs = " ".join(parblaslibname)
            else:
                sys.exit('parblaslibname is empty. This Blas/Lapack vendor seems not to provide'
                ' a list of multithreaded libraries, please disable blasmt or use a'
                ' multithreaded Blas implementation.')
            if 'parlapacklibname' in globals():
                lapack_libs = " ".join(parlapacklibname)
            else:
                sys.exit('parlapacklibname is empty. This Blas/Lapack vendor seems not to'
                ' provide a list of multithreaded libraries, please disable blasmt or'
                ' use a multithreaded Lapack implementation.')
        else:
            try:
                blas_libs = " ".join(blaslibname)
            except NameError:
                blas_libs = ''
            try:
                lapack_libs = " ".join(lapacklibname)
            except NameError:
                lapack_libs = ''
        try:
            blacs_libs = " ".join(blacslibname)
        except NameError:
            blacs_libs = ''
        try:
            scalapack_libs = " ".join(scalapacklibname)
        except NameError:
            scalapack_libs = ''

        mf.filter('^SCALAP  =.*', 'SCALAP  = '+scalapack_libs+' '+blacs_libs+' '+lapack_libs+' '+blas_libs)
        mf.filter('^LIBBLAS =.*', 'LIBBLAS = %s' % blas_libs)

        if '^mkl-scalapack' in spec:
            mf.filter('^OPTF\s*=.*', 'OPTF = -O  -DALLOW_NON_INIT -fPIC -m64 -I${MKLROOT}/include')
        else:
            mf.filter('^OPTF\s*=.*', 'OPTF = -O  -DALLOW_NON_INIT -fPIC')
        mf.filter('^OPTC\s*=.*', 'OPTC    = -O -fPIC')

        if spec.satisfies("%intel"):
            mf.filter('^OPTL\s*=', 'OPTL = -nofor-main ')

        if spec.satisfies('+mpi'):
            mpi = spec['mpi'].prefix
            try:
                mpicc = binmpicc
            except NameError:
                mpicc = 'mpicc'
            try:
                mpif90 = binmpif90
            except NameError:
                mpif90 = 'mpif90'
            mf.filter('CC\s*=.*', 'CC = %s  -g -fpic' % mpicc)
            mf.filter('FC\s*=.*', 'FC = %s  -g -fpic' % mpif90)
            mf.filter('FL\s*=.*', 'FL = %s  -g -fpic' % mpif90)
            mf.filter('^INCPAR.*', 'INCPAR = -I%s' % mpi.include)
            mf.filter('^LIBPAR.*', 'LIBPAR = $(SCALAP)')
        else:
            mf.filter('CC\s*=.*', 'CC = cc  -g -fpic')
            mf.filter('FC\s*=.*', 'FC = fc  -g -fpic')
            mf.filter('FL\s*=.*', 'FL = fc  -g -fpic')

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
        if spec.satisfies('~mpi~shared'):
            install('libseq/libmpiseq.a', prefix.lib)
        if spec.satisfies('~mpi+shared'):
            if platform.system() == 'Darwin':
                install('libseq/libmpiseq.dylib', prefix.lib)
            else:
                install('libseq/libmpiseq.so', prefix.lib)
        if spec.satisfies('+examples'):
            install_tree('examples', prefix + '/examples')

    # to use the existing version available in the environment: MUMPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        os.symlink("bin", prefix.bin) # bin dir does not exist but still need one for package installation to be complete
        os.symlink("include", prefix.include)
        os.symlink("lib", prefix.lib)
        if spec.satisfies('+examples'):
            os.symlink('examples', prefix + '/examples')
