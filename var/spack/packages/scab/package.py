from spack import *
import os
from subprocess import call

class Scab(Package):
    """A Finite Element library"""
    homepage = "http://www.dilbert.com"

    version('master', git=os.environ['SOFTWAREREPO1']+'scab.git', branch='master')
    version('1.6',    git=os.environ['SOFTWAREREPO1']+'scab.git', branch='v1.6')
    version('1.6.1',  git=os.environ['SOFTWAREREPO1']+'scab.git', tag='v1.6.1')

    variant('mkl'     , default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('shared', default=True, description='Build SCAB as a shared library')

    depends_on("mpf")
    depends_on("cblas", when='~mkl')
    depends_on("lapack", when='~mkl')
    depends_on("hdf5")
    depends_on("med-fichier")

    def install(self, spec, prefix):
        with working_dir('build', create=True):

            cmake_args = [
                "..",
                "-DCMAKE_INSTALL_PREFIX=../install",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]

            if spec.satisfies('%gcc'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug",
                                   "-DCMAKE_C_FLAGS=-fopenmp -D_GNU_SOURCE -pthread",
                                   '-DCMAKE_C_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread',
                                   '-DCMAKE_CXX_FLAGS=-pthread -fopenmp',
                                   '-DCMAKE_CXX_FLAGS_DEBUG=-g -fopenmp -D_GNU_SOURCE -pthread',
                                   '-DCMAKE_Fortran_FLAGS=-pthread -fopenmp',
                                   '-DCMAKE_Fortran_FLAGS_DEBUG=-g -fopenmp -pthread'])
            
            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            mpf = spec['mpf'].prefix
            cmake_args.extend(["-DMPF_DIR=%s/CMake" % mpf.share])

            hdf5 = spec['hdf5'].prefix
            cmake_args.extend(["-DHDF5_LIBRARY_DIRS=%s" % hdf5.lib])
            cmake_args.extend(["-DHDF5_INCLUDE_DIRS=%s" % hdf5.include])

            med = spec['med-fichier'].prefix
            cmake_args.extend(["-DMED_LIBRARY_DIRS=%s" % med.lib])
            cmake_args.extend(["-DMED_INCLUDE_DIRS=%s" % med.include])

            if spec.satisfies('~mkl'):

                cmake_args.extend(["-DMKL_DETECT=OFF"])
                cblas = spec['cblas'].prefix
                cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=%s/" % cblas.lib])
                cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=%s" % cblas.include])

                lapacke = spec['lapack'].prefix
                cmake_args.extend(["-DLAPACKE_LIBRARY_DIRS=%s/" % lapacke.lib])
                cmake_args.extend(["-DLAPACKE_INCLUDE_DIRS=%s" % lapacke.include])
            else:
                mklroot=os.environ['MKLROOT']
                cmake_args.extend(["-DMKL_DETECT=ON"])
                cmake_args.extend(["-DMKL_INCLUDE_DIRS=%s" % os.path.join(mklroot, "include") ])
                cmake_args.extend(["-DMKL_LIBRARY_DIRS=%s" % os.path.join(mklroot, "lib/intel64") ] )
                if spec.satisfies('%intel'):
                    cmake_args.extend(["-DMKL_LIBRARIES=mkl_intel_lp64;mkl_intel_thread;mkl_core " ] )
                else:
                    cmake_args.extend(["-DMKL_LIBRARIES=mkl_intel_lp64;mkl_gnu_thread;mkl_core " ] )
                cmake_args.extend(["-DBLAS_LIBRARIES=\"\" " ] )


            cmake_args.extend(std_cmake_args)
            call(["rm" , "-rf" , "CMake*"])
            cmake(*cmake_args)

            make()
            make("install")
