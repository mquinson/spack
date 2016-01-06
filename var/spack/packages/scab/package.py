from spack import *
import os
from subprocess import call

class Scab(Package):
    """
    A Finite Element Library.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    homepage = "http://www.google.com"

    try:
        version('nd',     git='hades:/home/falco/Airbus/scab.git', branch='master')
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'scab.git', branch='master')
        version('1.6',    git=repo+'scab.git', branch='v1.6')
        version('1.6.1',  git=repo+'scab.git', tag='v1.6.1')
    except KeyError:
        pass

    variant('shared', default=True, description='Build SCAB as a shared library')
    variant('hdf5',  default=False, description='Build SCAB with hdf5')

    depends_on("mpf")
    depends_on("cblas")
    depends_on("lapacke")
    depends_on("med-fichier", when="+hdf5")

    def install(self, spec, prefix):
        with working_dir('build', create=True):

            cmake_args = [
                "..",
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

            if spec.satisfies('%intel'):
                cmake_args.extend(['-DINTEL_LINK_FLAGS=-nofor-main'])       
     
            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            mpf = spec['mpf'].prefix
            cmake_args.extend(["-DMPF_DIR=%s/CMake" % mpf.share])

            if spec.satisfies('+hdf5'):
                med = spec['med-fichier'].prefix
                cmake_args.extend(["-DMED_LIBRARY_DIRS=%s" % med.lib])
                cmake_args.extend(["-DMED_INCLUDE_DIRS=%s" % med.include])

            if '^mkl-cblas' in spec:
                cmake_args.extend(["-DMKL_DETECT=ON"])
                mklblas = spec['mkl-blas'].prefix
                cmake_args.extend(["-DMKL_LIBRARY_DIRS=%s" % mklblas.lib])
                cmake_args.extend(["-DMKL_INCLUDE_DIRS=%s" % mklblas.include])
                mkl_libs=[]
                for l1 in blaslibname:
                    for l2 in l1.split(' '):
                        if l2.startswith('-l'):
                           mkl_libs.extend([l2[2:]])
                cmake_args.extend(["-DMKL_LIBRARIES=%s" % ";".join(mkl_libs)])
            else:
                cmake_args.extend(["-DMKL_DETECT=OFF"])
                cblas = spec['cblas'].prefix
                cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=%s/" % cblas.lib])
                cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=%s" % cblas.include])

                lapacke = spec['lapacke'].prefix
                cmake_args.extend(["-DLAPACKE_LIBRARY_DIRS=%s/" % lapacke.lib])
                cmake_args.extend(["-DLAPACKE_INCLUDE_DIRS=%s" % lapacke.include])
            
            cmake_args.extend(std_cmake_args)
            call(["rm" , "-rf" , "CMake*"])
            cmake(*cmake_args)

            make()
            make("install")
