from spack import *
import os
from subprocess import call

class Hmat(Package):
    """
    A Parallel H-Matrix C/C++ Library.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    homepage = "http://www.google.com"
    
    try:
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'hmat.git', branch='master')
    except KeyError:
        pass

    variant('starpu'  , default=True , description='Use StarPU library')
    # variant('pkg-config', default=False, description='Use pkg-config')
    variant('examples', default=True , description='Add examples to test library')
    variant('shared', default=True, description='Build HMAT as a shared library')

    depends_on("mpi")
    depends_on("starpu+mpi", when='+starpu')
    # depends_on("pkg-config")
    depends_on("cblas")
    depends_on("lapack")

    parallel = False

    def patch(self):
        # get hmat-oss
        call(["git" , "submodule" , "update", "--init"])
            
    def install(self, spec, prefix):
        with working_dir('build', create=True):

            cmake_args = [
                "..",
                "-DCMAKE_INSTALL_PREFIX=../install",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
            
            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            if spec.satisfies('+starpu'):
                mf = FileFilter('../CMake/config-parallel.h.in')
                mf.filter('^#cmakedefine HAVE_STARPU_NOWHERE', '//#cmakedefine HAVE_STARPU_NOWHERE')

            #    mf = FileFilter('../hmat-oss/CMake/FindCBLAS.cmake')
            #    mf.filter('\"cblas\"','"cblas;blas"')

            cblas = spec['cblas'].prefix
            cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=%s/" % cblas.include])
            cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=%s/" % cblas.lib])

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

            cmake_args.extend(std_cmake_args)
            call(["rm" , "-rf" , "CMake*"])
            cmake(*cmake_args)

            make()
            make("install")
