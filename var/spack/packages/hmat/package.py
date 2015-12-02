from spack import *
import os
from subprocess import call
import platform

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

    variant('starpu'  , default=True, description='Use StarPU library')
    variant('examples', default=True, description='Build and run examples at installation')
    variant('shared',   default=True, description='Build HMAT as a shared library')

    depends_on("mpi")
    depends_on("starpu+mpi", when='+starpu')
    depends_on("cblas")
    depends_on("lapack")

    parallel = False

    def patch(self):
        # get hmat-oss
        call(["git" , "submodule" , "update", "--init"])

    def install(self, spec, prefix):
        with working_dir('build', create=True):

            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args+=[
                "-DCMAKE_INSTALL_PREFIX=../install",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]

            if spec.satisfies('+examples'):
                cmake_args.extend(["-DBUILD_EXAMPLES:BOOL=ON"])

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            if '^mkl-cblas' in spec or '^mkl-lapack' in spec:
                cmake_args.extend(["-DMKL_DETECT=ON"])
            else:
                cmake_args.extend(["-DMKL_DETECT=OFF"])

                # To force FindCBLAS to find MY cblas
                mf = FileFilter('../hmat-oss/CMake/FindCBLAS.cmake')
                mf.filter('\"cblas\"','"%s"' % ";".join(cblaslibname+blaslibname))

                cblas = spec['cblas'].prefix
                cmake_args.extend(["-DCBLAS_INCLUDE_DIRS=" + cblas.include])
                cmake_args.extend(["-DCBLAS_LIBRARY_DIRS=" + cblas.lib])

                blas_libs = ";".join(blaslibname)
                blas = spec['blas'].prefix
                cmake_args.extend(["-DBLAS_LIBRARY_DIRS=" + blas.lib])
                cmake_args.extend(["-DBLAS_LIBRARIES=" + blas_libs])

                lapack_libs = ";".join(lapacklibname)
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
                make("test")
