from spack import *
import os
import platform
import spack
import shutil

class NetlibCblas(Package):
    """Netlib reference CBLAS"""
    homepage = "http://www.netlib.org/blas/#_cblas"

    version('3.6.0', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")
    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf',
            url="http://www.netlib.org/lapack/lapack-3.5.0.tgz")
    version('3.4.2', '61bf1a8a4469d4bdb7604f5897179478',
            url="http://www.netlib.org/lapack/lapack-3.4.2.tgz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('shared', default=True, description="Build shared library version")

    # virtual dependency
    provides('cblas')

    # blas is a virtual dependency.
    depends_on('blas')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    variant('shared', default=True, description="Build shared library version")

    def install(self, spec, prefix):

        mf = FileFilter('CBLAS/CMakeLists.txt')
        # patch to fix path to cblas cmake modules
        mf.filter('CMAKE/','cmake/')
        if spec.satisfies('%xl'):
            # patch to fix mangling with xl compiler, detection is not working
            mf.filter('#ADD_DEFINITIONS\( \"-D\$\{CDEFS\}\"\)','ADD_DEFINITIONS(-DADD_)')

        # Disable the building of lapack in CMakeLists.txt
        mf = FileFilter('CMakeLists.txt')
        mf.filter('add_subdirectory\(SRC\)','#add_subdirectory(SRC)')
        mf.filter('set\(ALL_TARGETS \$\{ALL_TARGETS\} lapack\)','#set(ALL_TARGETS ${ALL_TARGETS} lapack)')

        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        cmake_args.extend([
            "-Wno-dev",
            "-DBUILD_TESTING:BOOL=OFF",
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
            "-DCMAKE_INSTALL_LIBDIR=lib"])

        cmake_args.append('-DCBLAS=ON')

        blas_libs = spec['blas'].cc_link
        blas_libs = blas_libs.replace(' ', ';')
        cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])

        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
            if platform.system() == 'Darwin':
                cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')

        if spec.satisfies("%xl"):
            cmake_args.extend(["-DCMAKE_Fortran_FLAGS=-qextname"])

        cmake(*cmake_args)
        shutil.copy('CBLAS/include/cblas_mangling_with_flags.h', 'CBLAS/include/cblas_mangling.h')
        make()
        make("install")

    # to use the existing version available in the environment: CBLAS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('CBLAS_DIR'):
            netlibcblasroot=os.environ['CBLAS_DIR']
            if os.path.isdir(netlibcblasroot):
                os.symlink(netlibcblasroot+"/bin", prefix.bin)
                os.symlink(netlibcblasroot+"/include", prefix.include)
                os.symlink(netlibcblasroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(netlibcblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+netlibcblasroot+' ?')
        else:
            raise RuntimeError('CBLAS_DIR is not set, you must set this environment variable to the installation path of your netlib-cblas')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for netlib-cblas."""
        self.spec.cc_link="-L%s -lcblas" % self.spec.prefix.lib
        self.spec.fc_link=self.spec.cc_link