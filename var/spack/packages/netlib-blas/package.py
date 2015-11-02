from spack import *
import os


class NetlibBlas(Package):
    """Netlib reference BLAS"""
    homepage = "http://www.netlib.org/lapack/"
    url      = "http://www.netlib.org/lapack/lapack-3.5.0.tgz"

    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf')

    # virtual dependency
    provides('blas')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    variant('shared', default=True, description="Build shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-blas."""
        if spec.satisfies('+shared'):
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libblas.so")]
            module.blaslibfortname=[os.path.join(self.spec.prefix.lib, "libblas.so")]
        else:
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libblas.a")]
            module.blaslibfortname=[os.path.join(self.spec.prefix.lib, "libblas.a")]

    def install(self, spec, prefix):
        # Disable the building of lapack in CMakeLists.txt
        mf = FileFilter('CMakeLists.txt')
        mf.filter('add_subdirectory\(SRC\)','#add_subdirectory(SRC)')
        mf.filter('set\(ALL_TARGETS \$\{ALL_TARGETS\} lapack\)','#set(ALL_TARGETS ${ALL_TARGETS} lapack)')

        cmake_args = [
                ".",
                "-DBUILD_TESTING=OFF",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')

        cmake_args += std_cmake_args
        cmake(*cmake_args)
        make()
        make("install")
