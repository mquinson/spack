from spack import *
import os
import subprocess

class Maphys(Package):
    """a Massively Parallel Hybrid Solver."""
    homepage = "https://project.inria.fr/maphys/"
    url      = "http://maphys.gforge.inria.fr/maphys_0.9.2.tar.gz"

    version('0.9.2', '2dd5d4c21017b2277be93326705e2659',
            url='http://maphys.gforge.inria.fr/maphys_0.9.2.tar.gz')

    svnroot  = "https://scm.gforge.inria.fr/anonscm/svn/maphys/"
    version('svn-maphys_0.9.1',
            svn=svnroot+"branches/maphys_0.9.1")

    variant('mumps', default=False, description='Enable MUMPS direct solver')
    variant('pastix', default=True, description='Enable PASTIX direct solver')
    variant('examples', default=True, description='Enable compilation and installation of example executables')
    variant('mac', default=False, description='Patch the configuration to make it MAC OS X compatible')

    depends_on("mpi")
    depends_on("hwloc")
    depends_on("scotch+mpi")
    depends_on("blas")
    depends_on("lapack")
    depends_on("pastix+mpi", when='+pastix')
    depends_on("mumps", when='+mumps')
    depends_on("scalapack", when='+mumps')

    def setup(self):
        spec = self.spec
        mpi = spec['mpi'].prefix
        hwloc = spec['hwloc'].prefix
        scotch = spec['scotch'].prefix
        pastix = spec['pastix'].prefix
        blas = spec['blas'].prefix
        lapack = spec['lapack'].prefix

        if not os.path.isfile('Makefile.inc'):
            os.symlink('Makefile.inc.example', 'Makefile.inc')
        mf = FileFilter('Makefile.inc')

        mf.filter('prefix := /usr/local', 'prefix := %s' % spec.prefix)
        mf.filter('MPIFC := mpif90', 'MPIFC := mpif90 -I%s -ffree-form -ffree-line-length-0' % mpi.include)
        mf.filter('MPICC := mpicc', 'MPICC := mpicc -I%s' % mpi.include)
        mf.filter('MPIF77 := mpif77', 'MPIF77 := mpif77 -I%s' % mpi.include)

        if spec.satisfies('^mkl-blas'):
            mf.filter('# THREAD_FCFLAGS \+= -DMULTITHREAD_VERSION -openmp',
                      'THREAD_FCFLAGS += -DMULTITHREAD_VERSION -fopenmp')
            mf.filter('# THREAD_LDFLAGS := -openmp', 'THREAD_LDFLAGS := -fopenmp')

        lapack_libs = " ".join(lapacklibfortname)
        blas_libs = " ".join(blaslibfortname)
        if spec.satisfies('+mumps'):
            mumps = spec['mumps'].prefix
            #print os.path.isdir('%s' % mumps)
            #print mumps
            scalapack_libs = " ".join(scalapacklibfortname)
            mf.filter('MUMPS_prefix  :=  \$\(3rdpartyPREFIX\)/mumps/32bits', 'MUMPS_prefix  := %s' % mumps)
            mf.filter('MUMPS_LIBS := -L\$\{MUMPS_prefix\}/lib \$\(foreach a,\$\(ARITHS\),-l\$\(a\)mumps\) -lmumps_common -lpord', 'MUMPS_LIBS := -L${MUMPS_prefix}/lib $(foreach a,$(ARITHS),-l$(a)mumps) -lmumps_common -lpord '+scalapack_libs+' '+lapack_libs+' '+blas_libs)
        else:
            mf.filter('MUMPS_prefix  :=  \$\(3rdpartyPREFIX\)/mumps/32bits', '#MUMPS_prefix  := version without mumps')
            mf.filter('MUMPS_LIBS := -L\$\{MUMPS_prefix\}/lib \$\(foreach a,\$\(ARITHS\),-l\$\(a\)mumps\) -lmumps_common -lpord', 'MUMPS_LIBS  :=')
            mf.filter('MUMPS_FCFLAGS  :=  -DHAVE_LIBMUMPS', 'MUMPS_FCFLAGS  := ')
            mf.filter('MUMPS_FCFLAGS \+=  -I\$\{MUMPS_prefix\}/include', '#MUMPS_FCFLAGS += -I${MUMPS_prefix}/include')
            mf.filter('MUMPS_FCFLAGS \+= -DLIBMUMPS_USE_LIBSCOTCH', '#MUMPS_FCFLAGS += -DLIBMUMPS_USE_LIBSCOTCH')

        if spec.satisfies('+pastix'):
            pastix = spec['pastix'].prefix
            mf.filter('PASTIX_topdir := \$\(3rdpartyPREFIX\)/pastix/32bits', 'PASTIX_topdir := %s' % pastix)
            pastix_libs=subprocess.check_output([pastix+"/bin/pastix-conf", "--libs"])
            mf.filter('PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I\$\{PASTIX_topdir\}/install', 'PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I${PASTIX_topdir}/include')
            mf.filter('PASTIX_LIBS := -L\$\{PASTIX_topdir\}/install -lpastix -lrt', 'PASTIX_LIBS := %s ' % pastix_libs)
        else:
            mf.filter('PASTIX_topdir := \$\(3rdpartyPREFIX\)/pastix/32bits', '#PASTIX_topdir := %s')
            mf.filter('PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I\$\{PASTIX_topdir\}/install', '#PASTIX_FCFLAGS := -DHAVE_LIBPASTIX -I${PASTIX_topdir}/include')

        mf.filter('METIS_topdir  := \$\(3rdpartyPREFIX\)/metis/32bits', '#METIS_topdir  := version without metis')
        mf.filter('METIS_CFLAGS := -DHAVE_LIBMETIS -I\$\{METIS_topdir\}/Lib', 'METIS_CFLAGS := ')
        mf.filter('METIS_FCFLAGS := -DHAVE_LIBMETIS -I\$\{METIS_topdir\}/Lib', 'METIS_FCFLAGS := ')
        mf.filter('METIS_LIBS := -L\$\{METIS_topdir\} -lmetis', 'METIS_LIBS := ')

        mf.filter('SCOTCH_prefix := \$\(3rdpartyPREFIX\)/scotch_esmumps/32bits', 'SCOTCH_prefix  := %s' % scotch)
        mf.filter('SCOTCH_LIBS := -L\$\(SCOTCH_prefix\)/lib -lscotch -lscotcherrexit', 'SCOTCH_LIBS := -L$(SCOTCH_prefix)/lib -lptesmumps -lptscotch -lptscotcherr -lesmumps -lscotch -lscotcherr -lz -lm -lrt -pthread')

        blas = spec['blas'].prefix
        if spec.satisfies('^mkl-blas'):
            mf.filter('LMKLPATH   := /opt/intel/latest/mkl/lib/intel64', 'LMKLPATH   := %s' % blas)

        #if spec.satisfies('~mumps'):
        #    mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  :='+" ".join(scalapacklibparfortname))
        if spec.satisfies('^mkl-blas') and spec.satisfies('^mkl-lapack'):
            mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  :='+" ".join(lapacklibparfortname))

        #if spec.satisfies('~mumps') and not :
        #    mf.filter('^DALGEBRA_SEQUENTIAL_LIBS  :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  :='+" ".join(scalapackparfortname))
        if spec.satisfies('^mkl-blas') and spec.satisfies('^mkl-lapack'):
            mf.filter('^DALGEBRA_SEQUENTIAL_LIBS  :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  :='+" ".join(lapacklibfortname))

        if spec.satisfies('^mkl-blas') or spec.satisfies('^mkl-lapack') or spec.satisfies('^mkl-scalapack'):
            mf.filter('COMPIL_CFLAGS := -DAdd_', 'COMPIL_CFLAGS := -DAdd_ -m64 -I${MKLROOT}/include')
            mf.filter('FFLAGS := -g -O0', 'FFLAGS := -g -O0 -m64 -I${MKLROOT}/include')
            mf.filter('FCFLAGS := -g -O0', 'FCFLAGS := -g -O0 -DALLOW_NON_INIT -m64 -I${MKLROOT}/include')

        if spec.satisfies('^netlib-blas') and spec.satisfies('^netlib-lapack') and spec.satisfies('^netlib-scalapack') :
            dalgebralibs=''
            #if spec.satisfies('+mumps'):
            #    scalapack = spec['scalapack'].prefix
            #    dalgebralibs+='-L%s -lscalapack' % scalapack
            dalgebralibs+=' -L%s -ltmglib -llapack' % lapack
            dalgebralibs+=' -L%s -lblas' % blas
            mf.filter('^DALGEBRA_PARALLEL_LIBS  :=.*', 'DALGEBRA_PARALLEL_LIBS  := %s' % dalgebralibs)
            dalgebralibs='-L%s -llapack' % lapack + ' -L%s -lblas' % blas
            mf.filter('^DALGEBRA_SEQUENTIAL_LIBS :=.*', 'DALGEBRA_SEQUENTIAL_LIBS  := %s' % dalgebralibs)

        mf.filter('HWLOC_prefix := /usr/share', 'HWLOC_prefix := %s' % hwloc)

        mf.filter('ALL_FCFLAGS  :=  \$\(FCFLAGS\) -I\$\(abstopsrcdir\)/include -I. \$\(ALGO_FCFLAGS\) \$\(CHECK_FLAGS\)', 'ALL_FCFLAGS  :=  $(FCFLAGS) -I$(abstopsrcdir)/include -I. $(ALGO_FCFLAGS) $(CHECK_FLAGS) $(THREAD_FCFLAGS)')
        mf.filter('THREAD_FCLAGS', 'THREAD_LDFLAGS')

        if spec.satisfies('+mac'):
            mf.filter('-lrt', '');

    def install(self, spec, prefix):

        self.setup()
        make()
        if spec.satisfies('+examples'):
            make('check-examples')
        make("install")
        if spec.satisfies('+examples'):
            # examples are not installed by default
            install_tree('examples', '%s/lib/maphys/examples' % prefix)
