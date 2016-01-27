from spack import *
import spack
import os
import platform
from subprocess import call

class Actipole(Package):
    """
    A Finite Element Acoustic Solver.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir = spack.db.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = pkg_dir

    try:
        version('nd',     git='hades:/home/falco/Airbus/actipole.git', branch='master')
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'actipole.git', branch='master')
        version('1.21',   git=repo+'actipole.git', branch='v1.21')
        version('1.21.0', git=repo+'actipole.git', tag='v1.21.0')
    except KeyError:
        pass

    version('src', '7b878b76545ef9ddb6f2b61d4c4be833', url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('devel', git="/Users/sylvand/local/actipole", branch='master')

    variant('shared', default=True, description='Build ACTIPOLE as a shared library')

    depends_on("scab")
    depends_on("scab@src", when="@src")

    def install(self, spec, prefix):
        self.chdir_to_source("LOCAL_PATH")
        os.chdir("actipole")

        with working_dir('build', create=True):

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

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            scab = spec['scab'].prefix
            cmake_args.extend(["-DSCAB_DIR=%s/CMake" % scab.share])

            cmake(*cmake_args)

            make()
            make("install")
