from spack import *
import os

class Scalapack(Package):
    """A library of high-performance linear algebra routines for parallel distributed memory machines."""
    homepage = "http://www.netlib.org/scalapack/"
    url      = "http://www.netlib.org/scalapack/scalapack-2.0.0.tgz"

    version('2.0.2', '2f75e600a2ba155ed9ce974a1c4b536f')
    version('2.0.1', '17b8cde589ea0423afe1ec43e7499161')
    version('2.0.0', '9e76ae7b291be27faaad47cfc256cbfe')
    version('1.8.0', 'f4a3f3d7ef32029bd79ab8abcc026624')
    version('trunk', svn='https://icl.cs.utk.edu/svn/scalapack-dev/scalapack/trunk')

    depends_on("mpi")
    depends_on("blas")
    depends_on("lapack")

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):

            cmake_args = [
                "..",
                "-DBUILD_SHARED_LIBS=ON",
                "-DUSE_OPTIMIZED_LAPACK_BLAS=ON"]

            if "%gcc" in spec:
                cmake_args.extend(['-DBLAS_LIBRARIES=blas;m;gfortran'])

            cmake_args.extend(std_cmake_args)

            cmake(*cmake_args)
            make()
            make("install")
