from spack import *
import os
import sys

class HmatOss(Package):
    """A H-Matrix C/C++ library"""
    homepage = "https://github.com/jeromerobert/hmat-oss/"

    version('nd',     git='hades:/home/falco/Airbus/hmat-oss.git', branch='af/BinaryNestedDissection')
    version('master', git='https://github.com/jeromerobert/hmat-oss.git', branch='master')
    version('hmat-oss-1.1', git='https://github.com/jeromerobert/hmat-oss.git', branch='hmat-oss-1.1')
    version('git-1.1.2', git='https://github.com/jeromerobert/hmat-oss.git', tag='1.1.2')
    version('1.1.2', 'fe52fa22e413be862bec1b44a2b695a566525138', url='https://github.com/jeromerobert/hmat-oss/archive/1.1.2.tar.gz')

    variant('examples', default=True, description='Build examples at installation')

    depends_on("blas")
    depends_on("cblas")
    depends_on("lapack")
    depends_on("scotch", when="@nd")

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args+= [
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]

            if spec.satisfies('+scotch'):
                cmake_args.extend(["-DSCOTCH_DIR="+ spec['scotch'].prefix])

            if spec.satisfies('+examples'):
                cmake_args.extend(["-DBUILD_EXAMPLES:BOOL=ON"])

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

            cmake(*cmake_args)

            make()
            make("install")
