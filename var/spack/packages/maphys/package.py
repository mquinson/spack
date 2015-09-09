from spack import *
import os

class Maphys(Package):
    """a Massively Parallel Hybrid Solver."""
    homepage = "https://project.inria.fr/maphys/"
    url      = "http://maphys.gforge.inria.fr/maphys_0.9.2.tar.gz"

    version('0.9.2', 'e1d075374b13dd9e21906ca3fd41da7c')

    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('mumps', default=False, description='Enable MUMPS direct solver')

    depends_on("mpi")
    depends_on("hwloc")
    #depends_on("metis")
    depends_on("scotch")
    #depends_on("scotch_esmumps")
    depends_on("pastix")
    depends_on("mumps+scotch", when='+mumps')
    #depends_on("scalapack", when='~mkl')
    depends_on("blas", when='~mkl')
    depends_on("lapack", when='~mkl')

    def patch(self):
        spec = self.spec
        mpi = spec['mpi'].prefix
        hwloc = spec['hwloc'].prefix
        #metis = spec['metis'].prefix
        scotch = spec['scotch'].prefix
        #scotch = spec['scotch_esmumps'].prefix
        #mumps = spec['mumps'].prefix
        pastix = spec['pastix'].prefix
        if not spec.satisfies('+mkl'):
            #scalapack = spec['scalapack'].prefix
            lapack = spec['lapack'].prefix
            blas = spec['blas'].prefix

        os.symlink('Makefile.inc.example', 'Makefile.inc')
        mf = FileFilter('Makefile.inc')

        mf.filter('prefix := /usr/local', 'prefix := %s' % spec.prefix)
        mf.filter('MPIFC := mpif90', 'MPIFC := mpif90 -I%s -ffree-form -ffree-line-length-0' % mpi.include)
        mf.filter('MPICC := mpicc', 'MPICC := mpicc -I%s' % mpi.include)
        mf.filter('MPIF77 := mpif77', 'MPIF77 := mpif77 -I%s' % mpi.include)

        if spec.satisfies('+mkl'):
            mf.filter('# THREAD_FCFLAGS += -DMULTITHREAD_VERSION -fopenmp',
                      'THREAD_FCFLAGS += -DMULTITHREAD_VERSION')
            mf.filter('# THREAD_LDFLAGS := -openmp', 'THREAD_LDFLAGS := -fopenmp')

        if spec.satisfies('+mumps'):
            mumps = spec['mumps'].prefix
            scalapack = spec['scalapack'].prefix
            mf.filter('MUMPS_prefix  :=  \$\(3rdpartyPREFIX\)/mumps/32bits', 'MUMPS_prefix  := %s' % mumps)
            if spec.satisfies('+mkl'):
                mf.filter('MUMPS_LIBS := -L\$\{MUMPS_prefix\}/lib \$\(foreach a,\$\(ARITHS\),-l\$\(a\)mumps\) -lmumps_common -lpord', 'MUMPS_LIBS := -L${MUMPS_prefix}/lib $(foreach a,$(ARITHS),-l$(a)mumps) -lmumps_common -lpord -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_scalapack_lp64 -lmkl_gf_lp64 -lmkl_core -lmkl_intel_thread -lmkl_blacs_intelmpi_lp64 -liomp5 -ldl -lpthread -lm -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_gf_lp64 -lmkl_core -lmkl_intel_thread -liomp5 -ldl -lpthread -lm')
        else:
            mf.filter('MUMPS_prefix  :=  \$\(3rdpartyPREFIX\)/mumps/32bits', '#MUMPS_prefix  := version without mumps')
            mf.filter('MUMPS_LIBS := -L\$\{MUMPS_prefix\}/lib \$\(foreach a,\$\(ARITHS\),-l\$\(a\)mumps\) -lmumps_common -lpord', 'MUMPS_LIBS  :=')
            mf.filter('MUMPS_FCFLAGS  :=  -DHAVE_LIBMUMPS', 'MUMPS_FCFLAGS  := ')
            mf.filter('MUMPS_FCFLAGS \+=  -I\$\{MUMPS_prefix\}/include', '#MUMPS_FCFLAGS += -I${MUMPS_prefix}/include')
            mf.filter('MUMPS_FCFLAGS \+= -DLIBMUMPS_USE_LIBSCOTCH', '#MUMPS_FCFLAGS += -DLIBMUMPS_USE_LIBSCOTCH')

        mf.filter('PASTIX_topdir := \$\(3rdpartyPREFIX\)/pastix/32bits', 'PASTIX_topdir := %s' % pastix)
        mf.filter('PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I\$\{PASTIX_topdir\}/install', 'PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I${PASTIX_topdir}/include')
        if spec.satisfies('+mkl'):
            mf.filter('PASTIX_LIBS := -L\$\{PASTIX_topdir\}/install -lpastix -lrt', 'PASTIX_LIBS := -L${PASTIX_topdir}/install -lpastix -lrt -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm')

        #mf.filter('METIS_topdir  := \$\(3rdpartyPREFIX\)/metis/32bits', 'METIS_topdir  := %s' % metis)
        mf.filter('METIS_topdir  := \$\(3rdpartyPREFIX\)/metis/32bits', '#METIS_topdir  := version without metis')
        mf.filter('METIS_CFLAGS := -DHAVE_LIBMETIS -I\$\{METIS_topdir\}/Lib', 'METIS_CFLAGS := ')
        mf.filter('METIS_FCFLAGS := -DHAVE_LIBMETIS -I\$\{METIS_topdir\}/Lib', 'METIS_FCFLAGS := ')
        mf.filter('METIS_LIBS := -L\$\{METIS_topdir\} -lmetis', 'METIS_LIBS := ')

        mf.filter('SCOTCH_prefix := \$\(3rdpartyPREFIX\)/scotch_esmumps/32bits', 'SCOTCH_prefix  := %s' % scotch)
        mf.filter('SCOTCH_LIBS := -L\$\(SCOTCH_prefix\)/lib -lscotch -lscotcherrexit', 'SCOTCH_LIBS := -L$(SCOTCH_prefix)/lib -lscotch -lscotcherrexit -lz -lm -lrt -pthread')
        #mf.filter('SCOTCH_LIBS := -L\$\(SCOTCH_prefix\)/lib -lscotch -lscotcherrexit', 'SCOTCH_LIBS := -L$(SCOTCH_prefix)/lib -lptesmumps -lptscotch -lptscotcherr -lesmumps -lscotch -lscotcherr')

        if spec.satisfies('+mkl'):
            mf.filter('LMKLPATH   := /opt/intel/latest/mkl/lib/intel64', 'LMKLPATH   := ${MKLROOT}/lib/intel64')
            mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  := ${MKLROOT}/lib/intel64/libmkl_scalapack_lp64.a -Wl,--start-group ${MKLROOT}/lib/intel64/libmkl_intel_lp64.a ${MKLROOT}/lib/intel64/libmkl_core.a ${MKLROOT}/lib/intel64/libmkl_gnu_thread.a -Wl,--end-group ${MKLROOT}/lib/intel64/libmkl_blacs_openmpi_lp64.a -ldl -lpthread -lm -fopenmp')
            mf.filter('^DALGEBRA_SEQUENTIAL_LIBS  :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  := ${MKLROOT}/lib/intel64/libmkl_scalapack_lp64.a -Wl,--start-group ${MKLROOT}/lib/intel64/libmkl_intel_lp64.a ${MKLROOT}/lib/intel64/libmkl_core.a ${MKLROOT}/lib/intel64/libmkl_gnu_thread.a -Wl,--end-group ${MKLROOT}/lib/intel64/libmkl_blacs_openmpi_lp64.a -ldl -lpthread -lm -fopenmp')
            mf.filter('COMPIL_CFLAGS := -DAdd_', 'COMPIL_CFLAGS := -DAdd_ -m64 -I${MKLROOT}/include')
            mf.filter('FFLAGS := -g -O0', 'FFLAGS := -g -O0 -m64 -I${MKLROOT}/include')
            mf.filter('FCFLAGS := -g -O0', 'FCFLAGS := -g -O0 -DALLOW_NON_INIT -m64 -I${MKLROOT}/include')
        else:
            dalgebralibs=''
            if spec.satisfies('+mumps'):
                dalgebralibs+='-L%s -lscalapack' % scalapack
            dalgebralibs+=' -L%s -ltmglib -llapack' % lapack
            dalgebralibs+=' -L%s -lblas' % blas
            mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  := %s' % dalgebralibs)
            dalgebralibs='-L%s -llapack' % lapack + ' -L%s -lblas' % blas
            mf.filter('^DALGEBRA_SEQUENTIAL_LIBS :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  := %s' % dalgebralibs)

        mf.filter('HWLOC_prefix := /usr/share', 'HWLOC_prefix := %s' % hwloc)

    def install(self, spec, prefix):
        make()
        make('check-examples')
        make("install")
        # examples are not installed by default
        install_tree('examples', '%s/lib/maphys/examples' % prefix)
