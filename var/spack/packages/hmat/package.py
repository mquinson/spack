from spack import *
import spack
import os
import shutil
import sys
from subprocess import call
from subprocess import check_call
import platform
import spack

class Hmat(Package):
    """
    A Parallel H-Matrix C/C++ Library.
    Set the environment variable SOFTWARREEPO1 to get the versions.
    """
    pkg_dir  = spack.db.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = "file:"+join_path(pkg_dir, "empty.tar.gz")

    try:
        repo=os.environ['SOFTWAREREPO1']
        version('master', git=repo+'hmat.git', branch='master')
        version('1.2.1',  git=repo+'hmat.git', tag='v1.2.1')
    except KeyError:
        pass
    version('src')
    version('0',    git='hades:/home/falco/Airbus/hmat.git', branch='af/BinaryNestedDissection')
    version('nd',     git='hades:/home/falco/Airbus/hmat.git', branch='af/BinaryNestedDissection')

    variant('starpu'  , default=True , description='Use StarPU library')
    variant('examples', default=False, description='Build and run examples at installation')
    variant('shared',   default=True , description='Build HMAT as a shared library')

    depends_on("mpi")
    depends_on("starpu+mpi", when='+starpu')
    depends_on("cblas")
    depends_on("blas")
    depends_on("lapack")
    depends_on("scotch", when="@nd")

    if os.getenv("LOCAL_PATH"):
        project_local_path = os.environ["LOCAL_PATH"] + "/hmat"

    def patch(self):
        # get hmat-oss
        if self.spec.satisfies('@src'):
            return 0
        if os.environ.has_key("SPACK_HMATOSS_TAR"):
            check_call(["tar" , "xvf" , os.environ['SPACK_HMATOSS_TAR'] ])
        else:
            check_call(["git" , "submodule" , "update", "--init"])

    def install(self, spec, prefix):
        if self.spec.satisfies('@src') and os.path.exists('spack-build'):
                shutil.rmtree('spack-build')

        with working_dir('spack-build', create=True):
            cmake_args = [ ".." ]
            cmake_args.extend(std_cmake_args)
            cmake_args+=[
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DINSTALL_DATA_DIR:PATH=share",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"
                ]

            if '^scotch' in spec:
                scotch = spec['scotch'].prefix
                cmake_args+=[
                    "-DSCOTCH_DIR="+ scotch
                    ]
    
            if spec.satisfies('+examples'):
                cmake_args.extend(["-DBUILD_EXAMPLES:BOOL=ON"])

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            cmake_args.extend(["-DMKL_DETECT=OFF"])

            if '^mkl-blas' in spec or '^mkl-lapack' in spec:
                cmake_args.extend(["-DMKL_FOUND=ON"])
                mklblas = spec['mkl-blas'].prefix
                cmake_args.extend(["-DMKL_LIBRARY_DIRS=%s" % mklblas.lib])
                cmake_args.extend(["-DMKL_INCLUDE_DIRS=%s" % mklblas.include])
                cmake_args.extend(["-DMKL_LINKER_FLAGS=" + " ".join(blaslibname)])
                cmake_args.extend(["-DMKL_COMPILE_FLAGS="])
            else:
                cmake_args.extend(["-DMKL_FOUND=OFF"])

                # To allow compilation with netlib-cblas
                cmake_args.extend(["-DCBLAS_LIBRARIES=" + " ".join(cblaslibname)])

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
                make("test", "ARGS=-VV")
