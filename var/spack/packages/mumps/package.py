from spack import *
import os

class Mumps(Package):
    """a MUltifrontal Massively Parallel sparse direct Solver."""
    homepage = "http://mumps.enseeiht.fr/"
    url      = "http://mumps.enseeiht.fr/MUMPS_5.0.1.tar.gz"

    version('4.10.0', '959e9981b606cd574f713b8422ef0d9f')
    version('5.0.0', '3c6aeab847e9d775ca160194a9db2b75')
    version('5.0.1', 'b477573fdcc87babe861f62316833db0')

    variant('seq', default=False, description='Sequential version (no MPI)')
    variant('mkl', default=False, description='Use BLAS/ScaLAPACK from the Intel MKL library')
    variant('scotch', default=True, description='Enable Scotch')
    variant('ptscotch', default=False, description='Enable PT-Scotch')
    variant('metis', default=False, description='Enable Metis')
    #variant('parmetis', default=False, description='Enable parMetis')
    variant('mac', default=False, description='Patch the configuration to make it MAC OS X compatible')

    depends_on("mpi", when='~seq')
    depends_on("blas", when='~mkl')
    depends_on("scalapack", when='~mkl')
    depends_on("scotch", when='+scotch')
    depends_on("scotch+mpi", when='+ptscotch')
    depends_on("metis@5:", when='+metis')
    #depends_on("parmetis", when='+parmetis')

    def patch(self):
        spec = self.spec
        if spec.satisfies('~seq@5'):
            os.symlink('Make.inc/Makefile.debian.PAR', 'Makefile.inc')
        if spec.satisfies('+seq@5'):
            os.symlink('Make.inc/Makefile.debian.SEQ', 'Makefile.inc')
        if spec.satisfies('~seq@4'):
            os.symlink('Make.inc/Makefile.inc.generic', 'Makefile.inc')
        if spec.satisfies('+seq@4'):
            os.symlink('Make.inc/Makefile.inc.generic.SEQ', 'Makefile.inc')

        mf = FileFilter('Makefile.inc')

        ordlist='-Dpord'

        if spec.satisfies('~scotch'):
            mf.filter('^LSCOTCH   =.*', '#LSCOTCH   =')

        if spec.satisfies('~metis'):
            mf.filter('^IMETIS    =.*', '#IMETIS    =')
            mf.filter('^LMETIS    =.*', '#LMETIS    =')

        if spec.satisfies('+scotch'):
            scotch = spec['scotch'].prefix
            mf.filter('^LSCOTCHDIR =.*', 'LSCOTCHDIR = %s' % scotch.lib)
            mf.filter('^#ISCOTCH   =.*', 'ISCOTCH = -I%s' % scotch.include)
            ordlist+=' -Dscotch'

        if spec.satisfies('+ptscotch'):
            mf.filter('LSCOTCH   =.*', 'LSCOTCH   = -L$(LSCOTCHDIR) -lptesmumps -lptscotch -lptscotcherr -lesmumps -lscotch -lscotcherr')
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

        if spec.satisfies('~mkl'):
            scalapack = spec['scalapack'].prefix
            mf.filter('^SCALAP  =.*', 'SCALAP  = -L%s -lscalapack ' % scalapack.lib)
            blas = spec['blas'].prefix
            mf.filter('^LIBBLAS =.*', 'LIBBLAS = -L%s -lblas' % blas.lib)
            optf = 'OPTF = -O  -DALLOW_NON_INIT'

        if spec.satisfies('+mkl'):
            mf.filter('^SCALAP  =.*', 'SCALAP  = -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_gf_lp64 -lmkl_core -lmkl_intel_thread -lmkl_blacs_intelmpi_lp64 -liomp5 -ldl -lpthread -lm')
            mf.filter('^LIBBLAS =.*', 'LIBBLAS = -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_gf_lp64 -lmkl_core -lmkl_intel_thread -liomp5 -ldl -lpthread -lm')
            optf = 'OPTF = -O  -DALLOW_NON_INIT -m64 -I${MKLROOT}/include'

        optf+=' -fPIC'
        mf.filter('OPTF    = -O  -DALLOW_NON_INIT', '%s' % optf)
        mf.filter('OPTC    = -O', 'OPTC    = -O -fPIC')

        mpi = spec['mpi'].prefix
        mf.filter('CC\s*=.*', 'CC = mpicc')
        mf.filter('FC\s*=.*', 'FC = mpif90')
        mf.filter('FL\s*=.*', 'FL = mpif90')
        mf.filter('^INCPAR.*', 'INCPAR = -I%s' % mpi.include)
        mf.filter('^LIBPAR.*', 'LIBPAR = $(SCALAP)')

        mf.filter('^LIBOTHERS =.*', 'LIBOTHERS = -lz -lm -lrt -lpthread')

        if spec.satisfies('+mac'):
            mf.filter('-lrt', '');

    def install(self, spec, prefix):

        for app in ('s', 'd', 'c', 'z'):
            make(app)

        for app in ('sexamples', 'dexamples', 'cexamples', 'zexamples'):
            make(app)

        # No install provided
        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)
        if spec.satisfies('+seq'):
            install('libseq/libmpiseq.a', prefix.lib)
        install_tree('examples', '%s/lib/mumps/examples' % prefix)
