from spack import *
import spack
import os
import shutil
import platform
from subprocess import call

class Elfipole(Package):
    """
    A Finite Element Electromagnetism Solver.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir  = spack.repo.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = "file:"+join_path(pkg_dir, "empty.tar.gz")

    try:
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'elfipole.git', branch='master')
        version('1.21',   git=repo+'elfipole.git', branch='v1.21')
        version('1.21.0', git=repo+'elfipole.git', tag='v1.21.0')
    except KeyError:
        pass

    version('src')

    variant('shared', default=True, description='Build ELFIPOLE as a shared library')

    depends_on("scab")
    depends_on("scab@src", when="@src")
    depends_on('cmake')

    if os.getenv("LOCAL_PATH"):
        project_local_path = os.environ["LOCAL_PATH"] + "/elfipole"

    def build(self, spec, prefix):
        with working_dir('spack-build', create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            # Option for invoking the assembler on OSX (for sse/avx intrinsics)
            opt_ass=" -Wa,-q" if platform.system() == "Darwin" else ""

            if spec.satisfies('%gcc'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug",
                                   "-DCMAKE_C_FLAGS=-fopenmp -D_GNU_SOURCE -pthread"+opt_ass,
                                   '-DCMAKE_C_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread'+opt_ass,
                                   '-DCMAKE_CXX_FLAGS=-pthread -fopenmp'+opt_ass,
                                   '-DCMAKE_CXX_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread'+opt_ass,
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

            scab = spec['scab'].prefix
            cmake_args.extend(["-DSCAB_DIR=%s/CMake" % scab.share])

            cmake(*cmake_args)
            make()
            make("install")

    def install(self, spec, prefix):
        if self.spec.satisfies('@src') and os.path.exists('spack-build'):
            shutil.rmtree('spack-build')

        self.build(spec,prefix)
