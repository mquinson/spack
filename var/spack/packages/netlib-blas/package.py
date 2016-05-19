from spack import *
import os
import platform
import spack

class NetlibBlas(Package):
    """Netlib reference BLAS"""
    homepage = "http://www.netlib.org/lapack/"

    version('3.6.0', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")
    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf',
            url="http://www.netlib.org/lapack/lapack-3.5.0.tgz")
    version('3.4.2', '61bf1a8a4469d4bdb7604f5897179478',
            url="http://www.netlib.org/lapack/lapack-3.4.2.tgz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    # virtual dependency
    provides('blas')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    variant('shared', default=True, description="Build shared library version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-blas."""
        if os.path.isdir(spec.prefix.lib64):
            libdir = self.spec.prefix+"/lib64"
        if os.path.isdir(spec.prefix.lib):
            libdir = self.spec.prefix+"/lib"

        module.blaslibname=["-L%s -lblas" % libdir]
        module.blaslibfortname = module.blaslibname

    def install(self, spec, prefix):
        # Disable the building of lapack in CMakeLists.txt
        mf = FileFilter('CMakeLists.txt')
        mf.filter('add_subdirectory\(SRC\)','#add_subdirectory(SRC)')
        mf.filter('set\(ALL_TARGETS \$\{ALL_TARGETS\} lapack\)','#set(ALL_TARGETS ${ALL_TARGETS} lapack)')

        cmake_args = ["."]
        cmake_args+= std_cmake_args
        cmake_args+=[
                "-DBUILD_TESTING=OFF",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
            if platform.system() == 'Darwin':
                cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')
        cmake_args.append('-DCMAKE_INSTALL_LIBDIR=lib')

        cmake(*cmake_args)
        make()
        make("install")

    # to use the existing version available in the environment: BLAS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BLAS_DIR'):
            netlibblasroot=os.environ['BLAS_DIR']
            if os.path.isdir(netlibblasroot):
                os.symlink(netlibblasroot+"/bin", prefix.bin)
                os.symlink(netlibblasroot+"/include", prefix.include)
                os.symlink(netlibblasroot+"/lib", prefix.lib)
            else:
                sys.exit(netlibblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+netlibblasroot+' ?')
        else:
            sys.exit('BLAS_DIR is not set, you must set this environment variable to the installation path of your netlib-blas')
