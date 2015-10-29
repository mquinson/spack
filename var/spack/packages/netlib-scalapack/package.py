from spack import *
import os

class NetlibScalapack(Package):
    """A library of high-performance linear algebra routines for parallel distributed memory machines."""
    homepage = "http://www.netlib.org/scalapack/"
    url      = "http://www.netlib.org/scalapack/scalapack-2.0.0.tgz"

    version('2.0.2', '2f75e600a2ba155ed9ce974a1c4b536f')
    version('2.0.1', '17b8cde589ea0423afe1ec43e7499161')
    version('2.0.0', '9e76ae7b291be27faaad47cfc256cbfe')
    version('1.8.0', 'f4a3f3d7ef32029bd79ab8abcc026624')
    version('trunk', svn='https://icl.cs.utk.edu/svn/scalapack-dev/scalapack/trunk')

    # virtual dependency
    provides('scalapack')

    variant('shared', default=True, description="Use shared library version")

    depends_on("mpi")
    depends_on("blas")
    depends_on("lapack")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-scalapack."""
        if '+shared' in spec:
            module.scalapacklibname=[os.path.join(self.spec.prefix.lib, "libscalapack.so")]
        else:
            module.scalapacklibname=[os.path.join(self.spec.prefix.lib, "libscalapack.a")]

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):

            cmake_args = [
                "..",
                "-DUSE_OPTIMIZED_LAPACK_BLAS=ON"]

            if spec.satisfies('+shared'):
                cmake_args.extend(['-DBUILD_SHARED_LIBS=ON'])
            else:
                cmake_args.extend(['-DBUILD_SHARED_LIBS=OFF'])

            blas_libs = " ".join(blaslibname)
            lapack_libs = " ".join(lapacklibname)
            if spec.satisfies('%gcc'):
                cmake_args.extend(['-DBLAS_LIBRARIES='+blas_libs+';m;gfortran'])
            elif spec.satisfies('%icc'):
                cmake_args.extend(['-DBLAS_LIBRARIES='+blas_libs+';m'])
            cmake_args.extend(['-DLAPACK_LIBRARIES='+lapack_libs])

            cmake_args.extend(std_cmake_args)
            cmake(*cmake_args)
            make()
            make("install")
