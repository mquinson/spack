from spack import *
import os
import platform
import spack
import shutil

class Netlib(Package):
    """
    BLAS/LAPACK version 3.X is a comprehensive FORTRAN library that does
    linear algebra operations including matrix inversions, least
    squared solutions to linear sets of equations, eigenvector
    analysis, singular value decomposition, etc. It is a very
    comprehensive and reputable package that has found extensive
    use in the scientific community.
    """
    homepage = "http://www.netlib.org/lapack/"

    version('3.6.0', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")
    version('3.5.0', 'b1d3e3e425b2e44a06760ff173104bdf',
            url="http://www.netlib.org/lapack/lapack-3.5.0.tgz")
    version('3.4.2', '61bf1a8a4469d4bdb7604f5897179478',
            url="http://www.netlib.org/lapack/lapack-3.4.2.tgz")
    version('3.4.1', '44c3869c38c8335c2b9c2a8bb276eb55',
            url="http://www.netlib.org/lapack/lapack-3.4.1.tgz")
    version('3.4.0', '02d5706ec03ba885fc246e5fa10d8c70',
            url="http://www.netlib.org/lapack/lapack-3.4.0.tgz")
    version('3.3.1', 'd0d533ec9a5b74933c2a1e84eedc58b4',
            url="http://www.netlib.org/lapack/lapack-3.3.1.tgz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('shared', default=True, description="Build shared library version")

    # virtual dependency
    provides('blas')
    provides('lapack')
    provides('tmglib')
    provides('cblas')
    provides('lapacke')

    depends_on('cmake')

    # Doesn't always build correctly in parallel
    parallel = False

    # Null literal string is not permitted with xlf
    def patch_xlf(self):

        # xl does not accept empty strings
        mf = FileFilter('SRC/xerbla_array.f')
        mf.filter('SRNAME = \'\'', 'SRNAME = \' \'')
        mf = FileFilter('BLAS/SRC/xerbla_array.f')
        mf.filter('SRNAME = \'\'', 'SRNAME = \' \'')

        # fix mangling with xl compiler, detection is not working
        mf = FileFilter('CBLAS/CMakeLists.txt')
        mf.filter('#ADD_DEFINITIONS\( \"-D\$\{CDEFS\}\"\)','ADD_DEFINITIONS(-DADD_)')
        mf = FileFilter('LAPACKE/CMakeLists.txt')
        mf.filter('#ADD_DEFINITIONS\( \"-D\$\{CDEFS\}\"\)','ADD_DEFINITIONS(-DADD_)')


    def install(self, spec, prefix):

        if spec.satisfies('%xl'):
            self.patch_xlf()

        # patch to fix path to cblas cmake modules
        mf = FileFilter('CBLAS/CMakeLists.txt')
        mf.filter('CMAKE/','cmake/')
        # some lapack vendors do not provide geqrt so that we should
        # try another symbol to find lapack
        mf = FileFilter('CMakeLists.txt')
        mf.filter('dgeqrt', 'dgeqrf')

        # cmake configure
        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        cmake_args.extend([
            "-Wno-dev",
            "-DBUILD_TESTING:BOOL=OFF",
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

        # Enable cblas here.
        cmake_args.append('-DCBLAS=ON')
        # Enable lapacke here.
        cmake_args.extend(["-DLAPACKE=ON"])
        cmake_args.extend(["-DLAPACKE_WITH_TMG=ON"])

        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
            if platform.system() == 'Darwin':
                cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')
        cmake_args.append('-DCMAKE_INSTALL_LIBDIR=lib')

        if spec.satisfies("%xl"):
            cmake_args.extend(["-DCMAKE_Fortran_FLAGS=-qextname"])

        cmake(*cmake_args)
        # cp LAPACKE/include/lapacke_mangling_with_flags.h LAPACKE/include/lapacke_mangling.h
        shutil.copy('LAPACKE/include/lapacke_mangling_with_flags.h', 'LAPACKE/include/lapacke_mangling.h')
        make()
        make("install")

    # to use the existing version available in the environment: LAPACKE_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('LAPACKE_DIR'):
            netliblapackeroot=os.environ['LAPACKE_DIR']
            if os.path.isdir(netliblapackeroot):
                os.symlink(netliblapackeroot+"/bin", prefix.bin)
                os.symlink(netliblapackeroot+"/include", prefix.include)
                os.symlink(netliblapackeroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(netliblapackeroot+' directory does not exist.'+' Do you really have openmpi installed in '+netliblapackeroot+' ?')
        else:
            raise RuntimeError('LAPACKE_DIR is not set, you must set this environment variable to the installation path of your netlib-lapacke')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for netlib-lapacke."""
        self.spec.cc_link="-L%s -llapacke -llapack -ltmglib -lcblas -lblas" % self.spec.prefix.lib
        self.spec.fc_link=self.spec.cc_link