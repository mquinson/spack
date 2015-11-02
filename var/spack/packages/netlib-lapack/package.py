from spack import *
import os
class NetlibLapack(Package):
    """
    LAPACK version 3.X is a comprehensive FORTRAN library that does
    linear algebra operations including matrix inversions, least
    squared solutions to linear sets of equations, eigenvector
    analysis, singular value decomposition, etc. It is a very
    comprehensive and reputable package that has found extensive
    use in the scientific community.
    """
    homepage = "http://www.netlib.org/lapack/"
    url      = "http://www.netlib.org/lapack/lapack-3.5.0.tgz"

    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf')
    version('3.4.2', '61bf1a8a4469d4bdb7604f5897179478')
    version('3.4.1', '44c3869c38c8335c2b9c2a8bb276eb55')
    version('3.4.0', '02d5706ec03ba885fc246e5fa10d8c70')
    version('3.3.1', 'd0d533ec9a5b74933c2a1e84eedc58b4')

    variant('shared', default=True, description="Build shared library version")

    # virtual dependency
    provides('lapack')

    # blas is a virtual dependency.
    depends_on('blas')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-lapack."""
        if spec.satisfies('+shared'):
            module.lapacklibname=[os.path.join(self.spec.prefix.lib, "liblapack.so")]
            module.lapacklibfortname=[os.path.join(self.spec.prefix.lib, "liblapack.so")]
        else:
            module.lapacklibname=[os.path.join(self.spec.prefix.lib, "liblapack.a")]
            module.lapacklibfortname=[os.path.join(self.spec.prefix.lib, "liblapack.a")]

    def install(self, spec, prefix):
        blas_libs = ";".join(blaslibname)
        cmake_args = [
            ".", "-Wno-dev",
            '-DBLAS_LIBRARIES=' + blas_libs]

        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')

        cmake_args += std_cmake_args

        cmake(*cmake_args)
        make()
        make("install")
