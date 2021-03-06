from spack import *
import spack
import os
import shutil
from subprocess import call

class Mpf(Package):
    """
    A Parallel Linear Algebra Library.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir = spack.repo.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = "file:"+join_path(pkg_dir, "empty.tar.gz")

    try:
        version('nd',     git='hades:/home/falco/Airbus/mpf.git', branch='master')
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'mpf.git', branch='master')
        version('chameleon', git=repo+'mpf.git', branch='gs/chameleon')
        version('1.22',   git=repo+'mpf.git', branch='v1.22')
        version('1.22.0', git=repo+'mpf.git', tag='v1.22.0')
        version('1.23',   git=repo+'mpf.git', branch='v1.23')
        version('1.23.0', git=repo+'mpf.git', tag='v1.23.0')
    except KeyError:
        pass

    version('devel', git="/Users/sylvand/local/mpf", branch='gs/file_spido2')
    version('src')

    variant('shared', default=True , description='Build MPF as a shared library')
    variant('metis' , default=False, description='Use Metis')
    variant('python', default=False, description='Build MPF python interface')

    depends_on("py-mpi4py", when='+python')
    depends_on("blas")
    depends_on("lapack")
    depends_on("metis", when="+metis")
    depends_on("chameleon", when="@chameleon")
    depends_on("scotch +esmumps")
    depends_on("mumps +scotch")
    depends_on("pastix+mpi")
    depends_on("hmat")
    depends_on('cmake')

    if os.getenv("LOCAL_PATH"):
        project_local_path = os.environ["LOCAL_PATH"] + "/mpf"

    def build(self, spec, prefix):
        with working_dir('spack-build', create=True):
            scotch = spec['scotch'].prefix

            cmake_args = [
                "..",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
                "-DSCOTCH_INCLUDE_DIRS="+ scotch.include,
                "-DSCOTCH_LIBRARY_DIRS="+ scotch.lib,
                ]

            if spec.satisfies('%gcc'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug",
                                   "-DCMAKE_C_FLAGS=-fopenmp -D_GNU_SOURCE -pthread",
                                   '-DCMAKE_C_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread',
                                   '-DCMAKE_CXX_FLAGS=-pthread -fopenmp',
                                   '-DCMAKE_CXX_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread',
                                   '-DCMAKE_Fortran_FLAGS=-pthread -fopenmp',
                                   '-DCMAKE_Fortran_FLAGS_DEBUG=-g -fopenmp -pthread'])
            if spec.satisfies('%intel'):
                cmake_args.extend(["-DINTEL_LINK_FLAGS=-nofor-main",
                                   "-DCMAKE_BUILD_TYPE=Release",
                                   "-DCMAKE_C_FLAGS_RELEASE=-g -O -DNDEBUG -axCORE-AVX2,CORE-AVX-I,AVX,SSE4.2,SSE4.1,SSSE3,SSE3,SSE2 -openmp -D_GNU_SOURCE -pthread",
                                   "-DCMAKE_C_FLAGS=-openmp -D_GNU_SOURCE -pthread",
                                   "-DCMAKE_CXX_FLAGS_RELEASE=-I/usr/local/include/c++/4.8 -g -O -DNDEBUG -axCORE-AVX2,CORE-AVX-I,AVX,SSE4.2,SSE4.1,SSSE3,SSE3,SSE2 -openmp -D_GNU_SOURCE -pthread",
                                   "-DCMAKE_CXX_FLAGS=-I/usr/local/include/c++/4.8 -openmp -pthread",
                                   "-DCMAKE_Fortran_FLAGS_RELEASE=-g -O -assume byterecl -axCORE-AVX2,CORE-AVX-I,AVX,SSE4.2,SSE4.1,SSSE3,SSE3,SSE2 -openmp",
                                   "-DCMAKE_Fortran_FLAGS=-openmp",
                                   "-DULM_FORCE_DISABLED=ON"])

            # to activate the test building
            # cmake_args.extend(["-DMPF_TEST:BOOL=ON"])

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            if spec.satisfies('+python'):
                cmake_args.extend(['-DMPF_BUILD_PYTHON=ON'])
            else:
                cmake_args.extend(['-DMPF_BUILD_PYTHON=OFF'])

            hmat = spec['hmat'].prefix
            cmake_args.extend(["-DHMAT_DIR=%s/CMake" % hmat.share])
            cmake_args.extend(["-DENABLE_HMAT=ON"])

            try:
                blacs = spec['blacs'].prefix
                cmake_args.extend(["-DBLACS_LIBRARY_DIRS=" + blacs.lib])
            except KeyError:
                pass
            filter_file('BLACS REQUIRED', 'BLACS', '../CMakeLists.txt')

            pastix = spec['pastix'].prefix
            cmake_args.extend(["-DPASTIX_LIBRARY_DIRS=" + pastix.lib])
            cmake_args.extend(["-DPASTIX_INCLUDE_DIRS=" + pastix.include])
            cmake_args.extend(["-DENABLE_PASTIX=ON"])

            mumps = spec['mumps'].prefix
            # Workaround for the current bug in the hash calculation of mumps
            mumps = spec['mumps'].mumpsprefix
            cmake_args.extend(["-DMUMPS_LIBRARY_DIRS=" + mumps.lib])
            cmake_args.extend(["-DMUMPS_INCLUDE_DIRS=" + mumps.include])
            cmake_args.extend(["-DENABLE_MUMPS=ON"])

            if '^mkl' in spec:
                # cree les variables utilisees par as-make/CMake/FindMKL()
                cmake_args.extend(["-DMKL_DETECT=ON"])
                mklblas = spec['mkl'].prefix
                cmake_args.extend(["-DMKL_LIBRARY_DIRS=%s" % mklblas.lib])
                cmake_args.extend(["-DMKL_INCLUDE_DIRS=%s" % mklblas.include])
                mkl_libs=[]
                try:
                    blaslibname = spec['blas'].cc_link_mt
                except AttributeError:
                    blaslibname = spec['blas'].cc_link
                blaslibname = blaslibname.replace(' ', ';')
                for l1 in blaslibname:
                    for l2 in l1.split(' '):
                        if l2.startswith('-l'):
                           mkl_libs.extend([l2[2:]])
                cmake_args.extend(["-DMKL_LIBRARIES=%s" % ";".join(mkl_libs)])
            else:
                cmake_args.extend(["-DMKL_DETECT=OFF"])
                blas_libs = spec['blas'].cc_link
                blas_libs = blas_libs.replace(' ', ';')
                blas = spec['blas'].prefix
                cmake_args.extend(["-DBLAS_LIBRARY_DIRS=%s/" % blas.lib])
                cmake_args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])

                lapack_libs = spec['lapack'].cc_link
                lapack_libs = lapack_libs.replace(' ', ';')
                lapack = spec['lapack'].prefix
                cmake_args.extend(["-DLAPACK_LIBRARY_DIRS=%s/" % lapack.lib])
                cmake_args.extend(["-DLAPACK_LIBRARIES=%s" % lapack_libs])

            cmake_args.extend(["-DUSE_DEBIAN_OPENBLAS=OFF"])

            if spec.satisfies('@chameleon'):
                cmake_args.extend(["-DCHAMELEON_LIBRARY_DIRS="+ spec['chameleon'].prefix.lib])
                cmake_args.extend(["-DCHAMELEON_INCLUDE_DIRS="+ spec['chameleon'].prefix.include+'/chameleon'])

            if spec.satisfies('+metis'):
                cmake_args.extend(["-DMETIS_LIBRARY_DIRS="+ spec['metis'].prefix.lib])

            if os.environ.has_key("MKLROOT"):
                mklroot = os.environ['MKLROOT']
                if spec.satisfies('%gcc'):
                    mkl_thread = "mkl_gnu_thread"
                else:
                    mkl_thread = "mkl_intel_thread"
                cmake_args.extend(["-DMKL_LIBRARIES=mkl_intel_lp64;mkl_core;%s;" % mkl_thread])

                # problem with static library blacs...
                mf = FileFilter('../as-make/CMake/FindMKL.cmake')
                mf.filter('set\(MKL_LIBRARIES -Wl,--start-group;\$\{MKL_LIBRARIES\};-Wl,--end-group\)','set(MKL_LIBRARIES -Wl,--start-group,--whole-archive;${MKL_LIBRARIES};-Wl,--end-group,--no-whole-archive )')  

            cmake_args.extend(std_cmake_args)
            cmake(*cmake_args)

            make()
            make("install")

    def install(self, spec, prefix):
        if self.spec.satisfies('@src') and os.path.exists('spack-build'):
            shutil.rmtree('spack-build')

        self.build(spec,prefix)
