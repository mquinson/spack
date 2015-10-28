from spack import *
import os

class HmatOss(Package):
    """A H-Matrix C/C++ library"""
    homepage = "https://github.com/jeromerobert/hmat-oss/"

    version('master', git='https://github.com/jeromerobert/hmat-oss.git', branch='master')
    version('1.1.2', 'fe52fa22e413be862bec1b44a2b695a566525138', url='https://github.com/jeromerobert/hmat-oss/archive/1.1.2.tar.gz')

    variant('mkl', default=True, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('examples', default=True, description='Add examples to test library')

    depends_on("cblas", when='~mkl')

    def patch(self):
        with working_dir('CMake'):
            if os.path.isfile('Cache.in'):
                mf = FileFilter('Cache.in')
                spec = self.spec

                scotch = spec['scotch'].prefix
                mf.filter('^set (SCOTCH_HOME \"/usr/local\")', 'set (SCOTCH_HOME %s)' % scotch)
            
    def install(self, spec, prefix):
        with working_dir('build', create=True):
            cmake_args = [
                "..",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
            
            if os.path.isfile('../CMake/Cache.in'):
                cmake_args.extend(["-C ../CMake/Cache.in"])

            if spec.satisfies('+examples'):
                cmake_args.extend(["-DBUILD_EXAMPLES:BOOL=ON"])

            if spec.satisfies('~mkl'):
                cblas = spec['cblas'].prefix
                cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=%s/include" % cblas])
                cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=%s/lib" % cblas])
            else:
                mf = FileFilter('../CMake/FindMKL.cmake')
                mf.filter('set\(MKL_LINKER_FLAGS \"-L\$\{MKL_LIBRARY_DIR\} -lmkl_intel_\$\{MKL_IL\} -lmkl_core -lmkl_gnu_thread\"\)','set(MKL_LINKER_FLAGS "-L${MKL_LIBRARY_DIR} -lmkl_intel_${MKL_IL} -lmkl_core -lmkl_gnu_thread -lm")')

            cmake_args.extend(std_cmake_args)
            print cmake_args
            
            cmake(*cmake_args)

            make()
            make("install")
