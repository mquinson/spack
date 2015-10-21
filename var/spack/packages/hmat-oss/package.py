from spack import *
import os

class HmatOss(Package):
    """A H-Matrix C/C++ library"""
    homepage = "https://github.com/jeromerobert/hmat-oss/"

    # version('1.1.2', '8c697af7bd7424c2c27bb3fd765494d6a52ff724', url='https://github.com/jeromerobert/hmat-oss/archive/master.zip')
    version('master', git='https://github.com/jeromerobert/hmat-oss.git', branch='master')

    # variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')

    # depends_on("scotch")

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

            cmake_args.extend(std_cmake_args)
            # print cmake_args
            
            cmake(*cmake_args)

            make()
            make("install")
