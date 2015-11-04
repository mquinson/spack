from spack import *
import os
from subprocess import call
import platform

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

    depends_on("mpi", when='@2:')
    depends_on("blacs", when='@1.8.0')
    depends_on("blas")
    depends_on("lapack")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-scalapack."""
        if '+shared' in spec:
            if platform.system() == 'Darwin':
                module.scalapacklibname=[os.path.join(self.spec.prefix.lib, "libscalapack.dylib")]
            else:
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

            blas_libs = " ".join(blaslibfortname)
            blas_libs = blas_libs.replace(' ', ';')
            cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])

            lapack_libs = " ".join(lapacklibfortname)
            lapack_libs = lapack_libs.replace(' ', ';')
            cmake_args.extend(['-DLAPACK_LIBRARIES=%s' % lapack_libs])

            cmake_args.extend(std_cmake_args)
            cmake(*cmake_args)
            make()
            make("install")

    # Old version, like 1.8.0, dont use CMakeLists.txt
    @when('@1.8.0')
    def install(self, spec, prefix):
        call(['cp', 'SLmake.inc.example', 'SLmake.inc'])
        mf = FileFilter('SLmake.inc')
        mf.filter('home\s*=.*', 'home=%s' % os.getcwd())
        mf.filter('Df77IsF2C', 'DAdd_')
        if spec.satisfies('+shared'):
            mf.filter('CCFLAGS\s*=', 'CCFLAGS = -fPIC ')
            mf.filter('F77FLAGS\s*=', 'F77FLAGS = -fPIC ')
        make(parallel=False)
        mkdirp(prefix.lib)

        if spec.satisfies('+shared'):
            call(['cc', '-shared', '-o', 'libscalapack.so', '-Wl,--whole-archive', 'libscalapack.a', '-Wl,--no-whole-archive'])
            install('libscalapack.so', '%s/libscalapack.so' % prefix.lib)
        else:
            install('libscalapack.a', '%s/libscalapack.a' % prefix.lib)
