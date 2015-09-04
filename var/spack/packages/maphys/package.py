from spack import *
import os

class Maphys(Package):
    """a Massively Parallel Hybrid Solver."""
    homepage = "https://project.inria.fr/maphys/"
    url      = "http://maphys.gforge.inria.fr/maphys_0.9.2.tar.gz"

    version('0.9.2', 'e1d075374b13dd9e21906ca3fd41da7c')

    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')

    depends_on("mpi")
    depends_on("hwloc")
    depends_on("metis")
    depends_on("scotch_esmumps")
    depends_on("pastix")
    depends_on("mumps+scotch")
    depends_on("scalapack", when='~mkl')
    depends_on("blas", when='~mkl')
    depends_on("lapack", when='~mkl')

    def patch(self):
        spec = self.spec
        mpi = spec['mpi'].prefix
        hwloc = spec['hwloc'].prefix
        metis = spec['metis'].prefix
        scotch = spec['scotch_esmumps'].prefix
        mumps = spec['mumps'].prefix
        pastix = spec['pastix'].prefix
        if not spec.satisfies('+mkl'):
            scalapack = spec['scalapack'].prefix
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


        mf.filter('MUMPS_prefix  :=  \$\(3rdpartyPREFIX\)/mumps/32bits', 'MUMPS_prefix  := %s' % mumps)
        mf.filter('PASTIX_topdir := \$\(3rdpartyPREFIX\)/pastix/32bits', 'PASTIX_topdir := %s' % pastix)
        mf.filter('PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I\$\{PASTIX_topdir\}/install', 'PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I${PASTIX_topdir}/include')
        mf.filter('METIS_topdir  :=  \$\(3rdpartyPREFIX\)/metis/32bits', 'METIS_topdir  := %s' % metis)
        mf.filter('SCOTCH_prefix := \$\(3rdpartyPREFIX\)/scotch_esmumps/32bits', 'SCOTCH_prefix  := %s' % scotch)
        mf.filter('SCOTCH_LIBS := -L\$\(SCOTCH_prefix\)/lib -lscotch -lscotcherrexit', 'SCOTCH_LIBS := -L$(SCOTCH_prefix)/lib -lscotch -lscotcherrexit -lesmumps')

        if spec.satisfies('+mkl'):
            mf.filter('LMKLPATH   := /opt/intel/latest/mkl/lib/intel64', 'LMKLPATH   := ${MKLROOT}/lib/intel64')
            mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  := $(LMKLPATH)/libmkl_scalapack_lp64.a $(LMKLPATH)/libmkl_solver_lp64.a -Wl,--start-group $(LMKLPATH)/libmkl_gf_lp64.a $(LMKLPATH)/libmkl_core.a $(LMKLPATH)/libmkl_intel_thread.a -Wl,--end-group $(LMKLPATH)/libmkl_blacs_openmpi_lp64.a -liomp5 -ldl -lpthread -lm')
            mf.filter('^DALGEBRA_SEQUENTIAL_LIBS  :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  := -Wl,--start-group $(LMKLPATH)/libmkl_gf_lp64.a $(LMKLPATH)/libmkl_core.a $(LMKLPATH)/libmkl_sequential.a -Wl,--end-group -lpthread -lm')
            mf.filter('COMPIL_CFLAGS := -DAdd_', 'COMPIL_CFLAGS := -DAdd_ -m64 -I${MKLROOT}/include')
            mf.filter('FFLAGS := -g -O0', 'FFLAGS := -g -O0 -m64 -I${MKLROOT}/include')
            mf.filter('FCFLAGS := -g -O0', 'FCFLAGS := -g -O0 -m64 -I${MKLROOT}/include')
        else:
            dalgebralibs='-L%s -lscalapack' % scalapack
            dalgebralibs+=' -L%s -llapack' % lapack
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
