from spack import *
import os
import platform
import spack
import sys
from shutil import copyfile

class Pastix(Package):
    """a high performance parallel solver for very large sparse linear systems based on direct methods"""
    homepage = "http://pastix.gforge.inria.fr/files/README-txt.html"

    version('5.2.2.22', '85127ecdfaeed39e850c996b78573d94',
            url='https://gforge.inria.fr/frs/download.php/file/35070/pastix_5.2.2.22.tar.bz2')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/ricar/ricar.git', branch='master')
    version('develop', git='https://scm.gforge.inria.fr/anonscm/git/ricar/ricar.git', branch='develop')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('mpi', default=False, description='Enable MPI')
    variant('smp', default=True, description='Enable Thread')
    variant('blasmt', default=False, description='Enable to use multithreaded Blas library (MKL, ESSL, OpenBLAS)')
    variant('cuda', default=False, description='Enable CUDA kernels. Caution: only available if StarPU variant is enabled')
    variant('metis', default=False, description='Enable Metis')
    variant('starpu', default=False, description='Enable StarPU')
    variant('shared', default=True, description='Build Pastix as a shared library')
    variant('examples', default=True, description='Enable compilation and installation of example executables')
    variant('debug', default=False, description='Enable debug symbols')
    variant('idx64', default=False, description='To use 64 bits integers')
    variant('dynsched', default=False, description='Enable dynamic thread scheduling support')
    variant('memory', default=True, description='Enable memory usage statistics')
    variant('murgeup', default=False, description='Pull git murge source code (internet connection required), useful for the develop branch')

    depends_on("hwloc")
    depends_on("mpi", when='+mpi')
    depends_on("blas")
    depends_on("scotch")
    depends_on("scotch+idx64", when='+idx64')
    depends_on("metis@:4", when='+metis')
    depends_on("metis@:4+idx64", when='+metis+idx64')
    depends_on("starpu", when='+starpu')
    depends_on("starpu+mpi", when='+starpu+mpi')
    depends_on("starpu+cuda", when='+starpu+cuda')


    def patch_5_2_2_22(self):
        mf = FileFilter('example/src/makefile')
        mf.filter('^EXTRALIB       :=.*', 'EXTRALIB       :=  ${DST}/mem_trace.o ${EXTRALIB}')
        mf.filter('^EXTRALIB_MURGE :=.*', 'EXTRALIB_MURGE :=  ${DST}/mem_trace.o ${EXTRALIB_MURGE}')

    def setup(self):

        copyfile('config/LINUX-GNU.in', 'config.in')

        mf = FileFilter('config.in')
        spec = self.spec

        if spec.satisfies('+metis'):
            raise RuntimeError('You cannot use Metis and Scotch at the same'
             ' time because they are incompatible (Scotch provides a metis.h'
             ' which is not the same as the one providen by Metis)')

        # it seems we set CXXPROG twice but it is because in some
        # versions the line exists, and we can filter it, and in some
        # versions it does not
        if spec.satisfies('^starpu@1.2:') or spec.satisfies('^starpu@svn-trunk'):
            mf.filter('CCPROG      = gcc', 'CCPROG      = cc -Wall -DSTARPU_1_2\nCXXPROG     = c++')
        else:
            mf.filter('CCPROG      = gcc', 'CCPROG      = cc -Wall \nCXXPROG     = c++')

        mf.filter('CXXPROG     = g\+\+', 'CXXPROG     = c++')
        mf.filter('CFPROG      = gfortran', 'CFPROG      = f77')
        mf.filter('CF90PROG    = gfortran', 'CF90PROG    = f90')

        if spec.satisfies('%xl'):
            mf.filter('CCPROG      = cc -Wall', 'CCPROG      = cc -O2 -fPIC -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=pwr8')
            mf.filter('CXXPROG     = c\+\+', 'CXXPROG     = c++ -O2 -qsmp -fPIC  -qlanglvl=extended -qarch=auto -qhot -qtune=pwr8')
            mf.filter('CFPROG      = f77', 'CFPROG      = f77 -O2 -fPIC -qsmp -qextname -qhot -qtune=pwr8')
            mf.filter('CF90PROG    = fc', 'CF90PROG    = fc -O2 -qsmp -qextname -fPIC -qlanglvl=extended -qarch=auto -qhot -qtune=pwr8  -qlanglvl=90std')

        mf.filter('^# ROOT          =.*', 'ROOT          = %s' % spec.prefix)
        mf.filter('^# INCLUDEDIR    =.*', 'INCLUDEDIR    = ${ROOT}/include')
        mf.filter('^# LIBDIR        =.*', 'LIBDIR        = ${ROOT}/lib')
        mf.filter('^# BINDIR        =.*', 'BINDIR        = ${ROOT}/bin')
        mf.filter('^# PYTHON_PREFIX =.*', 'PYTHON_PREFIX = ${ROOT}')

        if spec.satisfies('%intel'):
            mf.filter('-lgfortran', '-lifcore')
            mf.filter('^CF90CCPOPT  =.*', 'CF90CCPOPT  = -fpp')
            mf.filter('-ffree-form', '')
            mf.filter('-x f95-cpp-input', '')

        if spec.satisfies('+shared'):
            mf.filter('#SHARED=1', 'SHARED=1')
            mf.filter('#SOEXT=\.so', 'SOEXT=.so')
            mf.filter('#SHARED_FLAGS =  -shared -Wl,-soname,__SO_NAME__', 'SHARED_FLAGS =  -shared')
            if platform.system() == 'Darwin':
                mf.filter('\.so', '.dylib')
                mf.filter('-shared -Wl,-soname,__SO_NAME__', '-shared')
            mf.filter('#CCFDEB       := \$\{CCFDEB\} -fPIC', 'CCFDEB       := ${CCFDEB} -fPIC')
            mf.filter('#CCFOPT       := \$\{CCFOPT\} -fPIC', 'CCFOPT       := ${CCFOPT} -fPIC')
            mf.filter('#CFPROG       := \$\{CFPROG\} -fPIC', 'CFPROG       := ${CFPROG} -fPIC')

        if spec.satisfies('+idx64'):
            mf.filter('#VERSIONINT  = _int64', 'VERSIONINT  = _int64')
            mf.filter('#CCTYPES     = -DINTSSIZE64', 'CCTYPES     = -DINTSSIZE64')
        else:
            mf.filter('#VERSIONINT  = _int32', 'VERSIONINT  = _int32')
            mf.filter('#CCTYPES     = -DINTSIZE32', 'CCTYPES     = -DINTSSIZE32')

        if spec.satisfies('~smp'):
            mf.filter('#VERSIONSMP  = _nosmp', 'VERSIONSMP  = _nosmp')
            mf.filter('#CCTYPES    := \$\(CCTYPES\) -DFORCE_NOSMP', 'CCTYPES    := $(CCTYPES) -DFORCE_NOSMP')

        if spec.satisfies('+memory'):
            mf.filter('#CCPASTIX   := \$\(CCPASTIX\) -DMEMORY_USAGE', 'CCPASTIX   := $(CCPASTIX) -DMEMORY_USAGE')

        if spec.satisfies('+dynsched'):
            mf.filter('#CCPASTIX   := \$\(CCPASTIX\) -DPASTIX_DYNSCHED', 'CCPASTIX   := $(CCPASTIX) -DPASTIX_DYNSCHED')

        if spec.satisfies('+mpi'):
            mpi = spec['mpi'].prefix
            try:
                mpicc = spec['mpi'].mpicc
            except NameError:
                mpicc = 'mpicc'
            try:
                mpicxx = spec['mpi'].mpicxx
            except NameError:
                mpicxx = 'mpic++'
            try:
                mpif90 = spec['mpi'].mpifc
            except NameError:
                mpif90 = 'mpif90'
            try:
                mpif77 = spec['mpi'].mpif77
            except NameError:
                mpif77 = 'mpif77'

            # it seems we set CXXPROG twice but it is because in some
            # versions the line exists, and we can filter it, and in
            # some versions it does not
            if spec.satisfies('^starpu@1.2:') or spec.satisfies('^starpu@svn-trunk'):
                mf.filter('^MPCCPROG    =.*', 'MPCCPROG    = %s -DSTARPU_1_2\nMPCXXPROG   = %s'%(mpicc, mpicxx))
            else:
                mf.filter('^MPCCPROG    =.*', 'MPCCPROG    = %s\nMPCXXPROG   = %s'%(mpicc, mpicxx))
            mf.filter('^MCFPROG     =.*', 'MCFPROG     = %s' % mpif90)
            mf.filter('MPCXXPROG   = mpic\+\+ -Wall', '')
            if '^simgrid' in spec:
                mf.filter('^#CCPASTIX   := \$\(CCPASTIX\) -DPASTIX_FUNNELED', 'CCPASTIX   := $(CCPASTIX) -DPASTIX_SINGLE')
        else:
            mf.filter('^#VERSIONMPI  = _nompi', 'VERSIONMPI  = _nompi')
            mf.filter('^#CCTYPES    := \$\(CCTYPES\) -DFORCE_NOMPI', 'CCTYPES    := $(CCTYPES) -DFORCE_NOMPI')
            mf.filter('MPCCPROG    =.*', 'MPCCPROG    = $(CCPROG)\nMPCXXPROG   = $(CXXPROG)')
            mf.filter('MPCXXPROG   =.*', 'MPCXXPROG   = $(CXXPROG)')
            mf.filter('MCFPROG     =.*', 'MCFPROG     = $(CFPROG)')

        if spec.satisfies('+starpu'):
            starpu = spec['starpu'].prefix
            if '^starpu+mpi' in spec:
                mf.filter('^#CCPASTIX   := \$\(CCPASTIX\) `pkg-config libstarpu --cflags` -DWITH_STARPU', 'CCPASTIX   := $(CCPASTIX) `pkg-config libstarpumpi --cflags` -DWITH_STARPU')
                mf.filter('^#EXTRALIB   := \$\(EXTRALIB\) `pkg-config libstarpu --libs`', 'EXTRALIB   := $(EXTRALIB) `pkg-config libstarpumpi --libs`')
            else:
                mf.filter('^#CCPASTIX   := \$\(CCPASTIX\) `pkg-config libstarpu --cflags` -DWITH_STARPU', 'CCPASTIX   := $(CCPASTIX) `pkg-config libstarpu --cflags` -DWITH_STARPU')
                mf.filter('^#EXTRALIB   := \$\(EXTRALIB\) `pkg-config libstarpu --libs`', 'EXTRALIB   := $(EXTRALIB) `pkg-config libstarpu --libs`')

        if spec.satisfies('+metis'):
            metis = spec['metis'].prefix
            metis_libs = spec['metis'].cc_link
            mf.filter('^#VERSIONORD  = _metis', 'VERSIONORD  = _metis')
            mf.filter('^#METIS_HOME  =.*', 'METIS_HOME  = %s' % metis)
            mf.filter('^#CCPASTIX   := \$\(CCPASTIX\) -DMETIS -I\$\(METIS_HOME\)/Lib', 'CCPASTIX   := $(CCPASTIX) -DMETIS -I$(METIS_HOME)/include')
            mf.filter('^#EXTRALIB   := \$\(EXTRALIB\) -L\$\(METIS_HOME\) -lmetis', 'EXTRALIB   := $(EXTRALIB) -L$(METIS_HOME)/lib -lmetis')

        scotch = spec['scotch'].prefix
        scotch_libs = spec['scotch'].cc_link
        mf.filter('^SCOTCH_HOME \?= \$\{HOME\}/scotch_5.1/', 'SCOTCH_HOME = %s' % scotch)
        if not spec.satisfies('^scotch+mpi'):
            mf.filter('#CCPASTIX   := \$\(CCPASTIX\) -I\$\(SCOTCH_INC\) -DWITH_SCOTCH',
                      'CCPASTIX   := $(CCPASTIX) -I$(SCOTCH_INC) -DWITH_SCOTCH')
            mf.filter('#EXTRALIB   := \$\(EXTRALIB\) -L\$\(SCOTCH_LIB\) -lscotch -lscotcherrexit',
                      'EXTRALIB   := $(EXTRALIB) -L$(SCOTCH_LIB) -lscotch -lscotcherrexit -lz -lm -lpthread')
            mf.filter('CCPASTIX   := \$\(CCPASTIX\) -I\$\(SCOTCH_INC\) -DDISTRIBUTED -DWITH_SCOTCH',
                      '#CCPASTIX   := $(CCPASTIX) -I$(SCOTCH_INC) -DDISTRIBUTED -DWITH_SCOTCH')
            mf.filter('EXTRALIB   := \$\(EXTRALIB\) -L\$\(SCOTCH_LIB\) -lptscotch -lscotch -lptscotcherrexit',
                      '#EXTRALIB   := $(EXTRALIB) -L$(SCOTCH_LIB) -lptscotch -lscotch -lptscotcherrexit')
        elif '^scotch@6:' in spec:
            mf.filter('EXTRALIB   := \$\(EXTRALIB\) -L\$\(SCOTCH_LIB\) -lptscotch -lscotch -lptscotcherrexit',
                      'EXTRALIB   := $(EXTRALIB) -L$(SCOTCH_LIB) -lptscotch -lscotch -lptscotcherrexit -lz -lm -lpthread')
        else:
            mf.filter('#EXTRALIB   := \$\(EXTRALIB\) -L\$\(SCOTCH_LIB\) -lptscotch -lptscotcherrexit',
                      'EXTRALIB   := $(EXTRALIB) -L$(SCOTCH_LIB) -lptscotch -lptscotcherrexit -lz -lm -lpthread')
            mf.filter('EXTRALIB   := \$\(EXTRALIB\) -L\$\(SCOTCH_LIB\) -lptscotch -lscotch -lptscotcherrexit',
                      '#EXTRALIB   := $(EXTRALIB) -L$(SCOTCH_LIB) -lptscotch -lscotch -lptscotcherrexit')
        hwloc = spec['hwloc'].prefix
        mf.filter('^HWLOC_HOME \?= /opt/hwloc/', 'HWLOC_HOME = %s' % hwloc)

        blas = spec['blas'].prefix
        blas_libs = spec['blas'].cc_link
        if spec.satisfies('+blasmt'):
            if '^mkl' in spec or '^essl' in spec or '^openblas+mt' in spec:
                blas_libs = spec['blas'].cc_link_mt
            else:
                raise RuntimeError('Only ^openblas+mt, ^mkl and ^essl provide multithreaded blas.')

        mf.filter('^BLASLIB  =.*', 'BLASLIB  = %s -lm' % blas_libs)
        mf.filter('LDFLAGS  = $(EXTRALIB) $(BLASLIB)', 'LDFLAGS  = $(BLASLIB) $(EXTRALIB)')

        if platform.system() == 'Darwin':
            mf.filter('-lrt', '')
            mf.filter('i686_pc_linux', 'i686_mac')

    def install(self, spec, prefix):

        with working_dir('src'):


            if spec.satisfies('@develop') or spec.satisfies('@src'):

                # some dumb pre-processing due to the dependency to murge (git)
                copyfile('config/LINUX-GNU.in', 'config.in')
                if spec.satisfies('+murgeup'):
                    # required to get murge sources "make murge_up"
                    make('murge_up')
                # this file must be generated
                make('sopalin/src/murge_fortran.c')

                with working_dir('spack-build', create=True):

                    cmake_args = [".."]
                    cmake_args.extend(std_cmake_args)
                    cmake_args.extend([
                        "-Wno-dev",
                        "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                        "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])
                    if spec.satisfies('+debug'):
                        # Enable Debug here.
                        cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
                    else:
                        cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])
                    if spec.satisfies('+shared'):
                        # Enable build shared libs.
                        cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])
                    else:
                        cmake_args.extend(["-DBUILD_SHARED_LIBS=OFF"])
                    if spec.satisfies('+examples'):
                        # Enable Examples here.
                        cmake_args.extend(["-DPASTIX_BUILD_EXAMPLES=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_BUILD_EXAMPLES=OFF"])
                    if spec.satisfies('+smp'):
                        cmake_args.extend(["-DPASTIX_WITH_MULTITHREAD=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_WITH_MULTITHREAD=OFF"])
                    if spec.satisfies('+mpi'):
                        # Enable MPI here.
                        cmake_args.extend(["-DPASTIX_WITH_MPI=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_WITH_MPI=OFF"])
                    if spec.satisfies('+starpu'):
                        # Enable StarPU here.
                        cmake_args.extend(["-DPASTIX_WITH_STARPU=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_WITH_STARPU=OFF"])
                    if spec.satisfies('+starpu') and spec.satisfies('+cuda'):
                        # Enable CUDA here.
                        cmake_args.extend(["-DPASTIX_WITH_STARPU_CUDA=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_WITH_STARPU_CUDA=OFF"])
                    if spec.satisfies('+metis'):
                        # Enable METIS here.
                        cmake_args.extend(["-DPASTIX_ORDERING_METIS=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_ORDERING_METIS=OFF"])
                    if spec.satisfies('+idx64'):
                        # Int of size 64bits.
                        cmake_args.extend(["-DPASTIX_INT64=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_INT64=OFF"])
                    if spec.satisfies('+dynsched'):
                        # Enable dynamic thread scheduling support.
                        cmake_args.extend(["-DPASTIX_DYNSCHED=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_DYNSCHED=OFF"])
                    if spec.satisfies('+memory'):
                        # Enable Memory statistics here.
                        cmake_args.extend(["-DPASTIX_WITH_MEMORY_USAGE=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_WITH_MEMORY_USAGE=OFF"])
                    if spec.satisfies('^scotch+mpi'):
                        # Enable distributed, required with ptscotch
                        cmake_args.extend(["-DPASTIX_DISTRIBUTED=ON"])
                    else:
                        cmake_args.extend(["-DPASTIX_DISTRIBUTED=OFF"])

                    if '^mkl-blas~shared' in spec:
                        cmake_args.extend(["-DBLA_STATIC=ON"])
                    if spec.satisfies('+blasmt'):
                        cmake_args.extend(["-DPASTIX_BLAS_MT=ON"])

                    blas = spec['blas'].prefix
                    blas_libs = spec['blas'].cc_link
                    cmake_args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])

                    cmake_args.extend(["-DCMAKE_VERBOSE_MAKEFILE=ON"])

                    if spec.satisfies("%xl"):
                        cmake_args.extend(["-DCMAKE_C_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])
                        cmake_args.extend(["-DCMAKE_Fortran_FLAGS=-qstrict -qsmp -qextname -qarch=auto -qhot -qtune=auto"])
                        cmake_args.extend(["-DCMAKE_CXX_FLAGS=-qstrict -qsmp -qlanglvl=extended -qarch=auto -qhot -qtune=auto"])


                    cmake(*cmake_args)
                    make()
                    make("install")

            else:

                self.patch_5_2_2_22()
                self.setup()
                if spec.satisfies('+debug'):
                    make('debug')
                else:
                    make()
                if spec.satisfies('+examples'):
                    make('examples')
                make("install")
                # examples are not installed by default
                if spec.satisfies('+examples'):
                    install_tree('example/bin', prefix + '/examples')
                    install_tree('matrix', prefix + '/matrix')


    # to use the existing version available in the environment: PASTIX_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        os.symlink("bin", prefix.bin)
        os.symlink("include", prefix.include)
        os.symlink("lib", prefix.lib)
