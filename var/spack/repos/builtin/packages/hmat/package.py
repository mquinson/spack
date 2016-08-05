from spack import *
import spack
import os
import shutil
import sys
import subprocess 
import platform
import spack

class Hmat(Package):
    """
    A Parallel H-Matrix C/C++ Library.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir  = spack.repo.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = "file:"+join_path(pkg_dir, "empty.tar.gz")

    try:
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'hmat.git', branch='master')
        version('1.2.1',  git=repo+'hmat.git', tag='v1.2.1')
        version('1.3',    git=repo+'hmat.git', branch='v1.3')
        version('1.3.0',  git=repo+'hmat.git', tag='v1.3.0')
    except KeyError:
        pass
    version('src')
    version('0',    git='hades:/home/falco/Airbus/hmat.git', branch='af/BinaryNestedDissection')
    version('nd',     git='hades:/home/falco/Airbus/hmat.git', branch='af/BinaryNestedDissection')

    variant('starpu'  , default=True , description='Use StarPU library')
    variant('examples', default=False, description='Build and run examples at installation')
    variant('shared',   default=True , description='Build HMAT as a shared library')

    depends_on("mpi")
    depends_on("starpu+mpi", when='+starpu')
    depends_on("cblas")
    depends_on("blas")
    depends_on("lapack")
    depends_on("scotch", when="@nd")
    depends_on('cmake')

    if os.getenv("LOCAL_PATH"):
        project_local_path = os.environ["LOCAL_PATH"] + "/hmat"

    def patch(self):
        # get hmat-oss
        if self.spec.satisfies('@src'):
            return 0
        if os.environ.has_key("SPACK_HMATOSS_TAR"):
            subprocess.check_call(["tar" , "xvf" , os.environ['SPACK_HMATOSS_TAR'] ])
        else:
            try:
                subprocess.check_call(["git" , "submodule" , "update", "--init"])
            except subprocess.CalledProcessError:
                # If github could not be contacted, we try to find the submodule hmat-oss in locally in SOFTWAREREPO1
                if os.environ.has_key("SOFTWAREREPO1"):
                    repo = os.environ['SOFTWAREREPO1']
                    for f in (FileFilter('.gitmodules'), FileFilter('.git/config')):
                        f.filter("https://github.com/jeromerobert/", "%s/" % repo)
                    subprocess.check_call(["git" , "submodule" , "update", "--init"])
                else:
                    raise

    def build(self, spec, prefix):
        with working_dir('spack-build'):
            make()
            make("install")

    def install(self, spec, prefix):
        if self.spec.satisfies('@src') and os.path.exists('spack-build'):
                shutil.rmtree('spack-build')

        with working_dir('spack-build', create=True):
            cmake_args = [ ".." ]
            cmake_args.extend(std_cmake_args)
            cmake_args+=[
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
                "-DCMAKE_BUILD_TYPE=debug"
                ]

            if '^scotch' in spec:
                scotch = spec['scotch'].prefix
                cmake_args+=[
                    "-DSCOTCH_DIR="+ scotch
                    ]

            if spec.satisfies('+examples'):
                cmake_args.extend(["-DBUILD_EXAMPLES:BOOL=ON"])

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

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            cmake_args.extend(["-DMKL_DETECT=OFF"])

            if '^mkl' in spec:
                cmake_args.extend(["-DMKL_FOUND=ON"])
                mklblas = spec['mkl'].prefix
                cmake_args.extend(["-DMKL_LIBRARY_DIRS=%s" % mklblas.lib])
                cmake_args.extend(["-DMKL_INCLUDE_DIRS=%s" % mklblas.include])
                cmake_args.extend(["-DMKL_LINKER_FLAGS=" + spec['blas'].cc_link])
                cmake_args.extend(["-DMKL_COMPILE_FLAGS="])
            else:
                cmake_args.extend(["-DMKL_FOUND=OFF"])

                # To allow compilation with netlib-cblas
                cmake_args.extend(["-DCBLAS_LIBRARIES=" + spec['cblas'].cc_link])

                cblas = spec['cblas'].prefix
                cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=" + cblas.include])
                cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=" + cblas.lib])

                blas_libs = spec['blas'].cc_link
                blas_libs = blas_libs.replace(' ', ';')
                blas = spec['blas'].prefix
                cmake_args.extend(["-DBLAS_LIBRARY_DIRS=" + blas.lib])
                cmake_args.extend(["-DBLAS_LIBRARIES=" + blas_libs])

                lapack_libs = spec['lapack'].cc_link
                lapack_libs = lapack_libs.replace(' ', ';')
                lapack = spec['lapack'].prefix
                cmake_args.extend(["-DLAPACK_LIBRARY_DIRS=" + lapack.lib])
                cmake_args.extend(["-DLAPACK_LIBRARIES=" + lapack_libs])

            cmake_args.extend(["-DUSE_DEBIAN_OPENBLAS=OFF"])

            if platform.system() == 'Darwin':
                filter_file('_LINK_HMAT_OSS LINK_PRIVATE.*', '_LINK_HMAT_OSS LINK_PRIVATE -Wl,-force_load,${_HMAT_OSS_PATH}  ${hmat-oss_LIB_DEPENDS})', '../CMakeLists.txt')

            cmake(*cmake_args)

            make()
            make("install")
            if spec.satisfies('+examples'):
                make("test", "ARGS=-VV")
