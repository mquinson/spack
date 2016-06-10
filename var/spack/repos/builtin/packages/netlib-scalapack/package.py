from spack import *
import os
from subprocess import call
import platform
import spack

class NetlibScalapack(Package):
    """A library of high-performance linear algebra routines for parallel distributed memory machines."""
    homepage = "http://www.netlib.org/scalapack/"

    version('2.0.2', '2f75e600a2ba155ed9ce974a1c4b536f',
            url="http://www.netlib.org/scalapack/scalapack-2.0.2.tgz")
    version('2.0.1', '17b8cde589ea0423afe1ec43e7499161',
            url="http://www.netlib.org/scalapack/scalapack-2.0.1.tgz")
    version('2.0.0', '9e76ae7b291be27faaad47cfc256cbfe',
            url="http://www.netlib.org/scalapack/scalapack-2.0.0.tgz")
    version('trunk', svn='https://icl.cs.utk.edu/svn/scalapack-dev/scalapack/trunk')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    # virtual dependency
    provides('blacs')
    provides('scalapack')

    variant('shared', default=True, description="Use shared library version")

    depends_on("cmake", when='@2.0.0:')
    depends_on("mpi", when='@2:')
    depends_on("blas")
    depends_on("lapack")

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):

            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DBUILD_TESTING:BOOL=OFF",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            cmake_args+=["-DUSE_OPTIMIZED_LAPACK_BLAS=ON"]
            cmake_args.extend([
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
                cmake_args.extend(['-DBUILD_STATIC_LIBS=OFF'])
                if platform.system() == 'Darwin':
                    cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            blas_libs = spec['blas'].fc_link
            blas_libs = blas_libs.replace(' ', ';')
            cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])

            lapack_libs = spec['lapack'].fc_link
            lapack_libs = lapack_libs.replace(' ', ';')
            cmake_args.extend(['-DLAPACK_LIBRARIES=%s' % lapack_libs])

            cmake(*cmake_args)
            make()
            make("install")

    # to use the existing version available in the environment: SCALAPACK_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('SCALAPACK_DIR'):
            netlibscalapackroot=os.environ['SCALAPACK_DIR']
            if os.path.isdir(netlibscalapackroot):
                os.symlink(netlibscalapackroot+"/bin", prefix.bin)
                os.symlink(netlibscalapackroot+"/include", prefix.include)
                os.symlink(netlibscalapackroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(netlibscalapackroot+' directory does not exist.'+' Do you really have openmpi installed in '+netlibscalapackroot+' ?')
        else:
            raise RuntimeError('SCALAPACK_DIR is not set, you must set this environment variable to the installation path of your netlib-scalapack')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for netlib-scalapack."""
        self.spec.cc_link = '-L%s -lscalapack' % self.spec.prefix.lib