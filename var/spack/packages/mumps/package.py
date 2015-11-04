from spack import *
import os
import platform

class Mumps(Package):
    """a MUltifrontal Massively Parallel sparse direct Solver."""
    homepage = "http://mumps.enseeiht.fr/"
    url      = "http://mumps.enseeiht.fr/MUMPS_5.0.1.tar.gz"

    version('4.10.0', '959e9981b606cd574f713b8422ef0d9f')
    version('5.0.0', '3c6aeab847e9d775ca160194a9db2b75')
    version('5.0.1', 'b477573fdcc87babe861f62316833db0')

    variant('seq', default=False, description='Sequential version (no MPI)')
    variant('scotch', default=False, description='Enable Scotch')
    variant('ptscotch', default=False, description='Enable PT-Scotch')
    variant('metis', default=False, description='Enable Metis')
    #variant('parmetis', default=False, description='Enable parMetis')
    variant('shared', default=True, description='Build MUMPS as a shared library')

    depends_on("mpi", when='~seq')
    depends_on("blas")
    depends_on("scalapack")
    depends_on("scotch", when='+scotch')
    depends_on("scotch+mpi", when='+ptscotch')
    depends_on("metis@5:", when='+metis')
    #depends_on("parmetis", when='+parmetis')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for Mumps."""
        libdir = self.spec.prefix.lib
        mumpslibname  = [os.path.join(libdir, "libsmumps.a")]
        mumpslibname += [os.path.join(libdir, "libdmumps.a")]
        mumpslibname += [os.path.join(libdir, "libcmumps.a")]
        mumpslibname += [os.path.join(libdir, "libzmumps.a")]
        mumpslibname += [os.path.join(libdir, "libmumps_common.a")]
        mumpslibname += [os.path.join(libdir, "libpord.a")]
        module.mumpslibname = mumpslibname

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
            mf.filter('^LSCOTCHDIR =.*', 'LSCOTCHDIR = %s' % scotch.lib)
            mf.filter('^#ISCOTCH   =.*', 'ISCOTCH = -I%s' % scotch.include)
            ordlist+=' -Dscotch'

        if spec.satisfies('+ptscotch'):
            scotch = spec['scotch'].prefix
            mf.filter('LSCOTCH   =.*', 'LSCOTCH   = -L$(LSCOTCHDIR) -lptesmumps -lptscotch -lptscotcherr -lesmumps -lscotch -lscotcherr')
            mf.filter('^#ISCOTCH   =.*', 'ISCOTCH = -I%s' % scotch.include)
            ordlist+=' -Dptscotch'

        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            mf.filter('^LMETISDIR =.*', 'LMETISDIR = %s' % metis.lib)
            mf.filter('^IMETIS    =.*', 'IMETIS    = -I%s' % metis.include)
            ordlist+=' -Dmetis'

        if spec.satisfies('+parmetis'):
            parmetis = spec['parmetis'].prefix
            mf.filter('^LMETISDIR =.*', 'LMETISDIR = %s' % parmetis.lib)
            mf.filter('^IMETIS    =.*', 'IMETIS = -I%s' % parmetis.include)
            mf.filter('^LMETIS    =.*', 'LMETIS = -L$(LMETISDIR) -lparmetis')
            ordlist+=' -Dparmetis'

        mf.filter('ORDERINGSF = -Dmetis -Dpord -Dscotch', 'ORDERINGSF = %s' % ordlist)

        if spec.satisfies('~scotch') and spec.satisfies('~ptscotch') :
            mf.filter('^LSCOTCH   =.*', '#LSCOTCH   =')

        if spec.satisfies('~metis'):
            mf.filter('^IMETIS    =.*', '#IMETIS    =')
            mf.filter('^LMETIS    =.*', '#LMETIS    =')

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
        mf.filter('CC\s*=.*', 'CC = mpicc')
        mf.filter('FC\s*=.*', 'FC = mpif90')
        mf.filter('FL\s*=.*', 'FL = mpif90')
        mf.filter('^INCPAR.*', 'INCPAR = -I%s' % mpi.include)
        mf.filter('^LIBPAR.*', 'LIBPAR = $(SCALAP)')

        mf.filter('^LIBOTHERS =.*', 'LIBOTHERS = -lz -lm -lrt -lpthread')

        if spec.satisfies('+shared'):
            mf.filter('^AR\s*=.*', 'AR=$(FC) -shared -o ')
            mf.filter('^RANLIB\s*=.*', 'RANLIB=echo ')
            mf.filter('^LIBEXT\s*=.*', 'LIBEXT = .so')
        if platform.system() == 'Darwin':
            mf.filter('-lrt', '');

    def install(self, spec, prefix):

        self.setup()

        for app in ('s', 'd', 'c', 'z'):
            make(app)

        for app in ('sexamples', 'dexamples', 'cexamples', 'zexamples'):
            make(app)

        # No install provided
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        if spec.satisfies('+seq~shared'):
            install('libseq/libmpiseq.a', prefix.lib)
        if spec.satisfies('+seq+shared'):
            install('libseq/libmpiseq.so', prefix.lib)
        install_tree('examples', '%s/lib/mumps/examples' % prefix)
