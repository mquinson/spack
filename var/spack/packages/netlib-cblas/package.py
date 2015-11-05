from spack import *
import os
import platform 

class NetlibCblas(Package):
    """The BLAS (Basic Linear Algebra Subprograms) are routines that
       provide standard building blocks for performing basic vector and
       matrix operations."""

    homepage = "http://www.netlib.org/blas/_cblas/"

    # tarball has no version, but on the date below, this MD5 was correct.
    version('2015-06-06', '1e8830f622d2112239a4a8a83b84209a',
            url='http://www.netlib.org/blas/blast-forum/cblas.tgz')

    variant('shared', default=True, description='Build CBLAS as a shared library')

    # virtual dependency
    provides('cblas')

    # blas is a virtual dependency.
    depends_on('blas')

    parallel = False

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-cblas."""

        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                module.cblaslibname=[os.path.join(self.spec.prefix.lib, "libcblas.dylib")]
            else:
                module.cblaslibname=[os.path.join(self.spec.prefix.lib, "libcblas.so")]
        else:
            module.cblaslibname=[os.path.join(self.spec.prefix.lib, "libcblas.a")]
        module.cblaslibfortname = module.cblaslibname

    def setup(self):
        spec = self.spec
        mf = FileFilter('Makefile.in')

        blas_libs = " ".join(blaslibfortname)
        mf.filter('^BLLIB =.*', 'BLLIB = %s' % blas_libs)
        mf.filter('^CC =.*', 'CC = cc')
        mf.filter('^FC =.*', 'FC = f90')
        mf.filter('^CFLAGS =', 'CFLAGS = -fPIC ')
        mf.filter('^FFLAGS =', 'FFLAGS = -fPIC ')

        if spec.satisfies('+shared'):
            mf.filter('^ARCH\s*=.*', 'ARCH=$(CC) $(BLLIB)')
            mf.filter('^ARCHFLAGS\s*=.*', 'ARCHFLAGS=-shared -o')
            mf.filter('^RANLIB\s*=.*', 'RANLIB=echo')
            mf.filter('^CCFLAGS\s*=', 'CCFLAGS = -fPIC ')
            mf.filter('^FFLAGS\s*=', 'FFLAGS = -fPIC ')
            mf.filter('\.a', '.so')

    def install(self, spec, prefix):

        self.setup()
        make('all')
        mkdirp(prefix.lib)
        mkdirp(prefix.include)

        # Rename the generated lib file to libcblas
        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                install('./lib/cblas_LINUX.so', '%s/libcblas.dylib' % prefix.lib)
            else:
                install('./lib/cblas_LINUX.so', '%s/libcblas.so' % prefix.lib)
        else:
            install('./lib/cblas_LINUX.a', '%s/libcblas.a' % prefix.lib)
        install('./include/cblas.h','%s' % prefix.include)
        install('./include/cblas_f77.h','%s' % prefix.include)
