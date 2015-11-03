from spack import *
import os
from subprocess import call

class Mpf(Package):
    """An parallel linear algebra library"""
    homepage = "http://www.dilbert.com"

    version('master', git=os.environ['SOFTWAREREPO1']+'mpf.git', branch='master')
    version('1.22', git=os.environ['SOFTWAREREPO1']+'mpf.git', branch='v1.22')
    version('1.22.0', git=os.environ['SOFTWAREREPO1']+'mpf.git', tag='v1.22.0')

    variant('mkl'     , default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('shared', default=True, description='Build MPF as a shared library')

    depends_on("py-mpi4py")
    depends_on("blas", when='~mkl')
    depends_on("lapack", when='~mkl')
    depends_on("mumps")
    depends_on("pastix")
    depends_on("hmat")
    depends_on("blacs")

    def install(self, spec, prefix):
        with working_dir('build', create=True):

            cmake_args = [
                "..",
                "-DCMAKE_INSTALL_PREFIX=../install",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]

            # to activate the test building
            # cmake_args.extend(["-DMPF_TEST:BOOL=ON"])
            
            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            hmat = spec['hmat'].prefix
            cmake_args.extend(["-DHMAT_DIR=%s/CMake" % hmat.share])
            cmake_args.extend(["-DENABLE_HMAT=ON"])

            blacs = spec['blacs'].prefix
            cmake_args.extend(["-DBLACS_LIBRARY_DIRS=%s/" % blacs.lib])

            pastix = spec['pastix'].prefix
            cmake_args.extend(["-DPASTIX_LIBRARY_DIRS=%s" % pastix.lib])
            cmake_args.extend(["-DPASTIX_INCLUDE_DIRS=%s" % pastix.include])
            cmake_args.extend(["-DENABLE_PASTIX=ON"])

            mumps = spec['mumps'].prefix
            cmake_args.extend(["-DMUMPS_LIBRARY_DIRS=%s" % mumps.lib])
            cmake_args.extend(["-DMUMPS_INCLUDE_DIRS=%s" % mumps.include])
            cmake_args.extend(["-DENABLE_MUMPS=ON"])

            if spec.satisfies('~mkl'):

                blas_libs = ";".join(blaslibname)
                blas = spec['blas'].prefix
                cmake_args.extend(["-DBLAS_LIBRARY_DIRS=%s/" % blas.lib])
                cmake_args.extend(["-DBLAS_LIBRARIES=%s" % blas_libs])

                lapack_libs = ";".join(lapacklibname)
                lapack = spec['lapack'].prefix
                cmake_args.extend(["-DLAPACK_LIBRARY_DIRS=%s/" % lapack.lib])
                cmake_args.extend(["-DLAPACK_LIBRARIES=%s" % lapack_libs])
                cmake_args.extend(["-DMKL_DETECT=OFF"])
                cmake_args.extend(["-DUSE_DEBIAN_OPENBLAS=OFF"])
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
