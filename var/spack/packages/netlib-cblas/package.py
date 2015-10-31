from spack import *
import os

class NetlibCblas(Package):
    """The BLAS (Basic Linear Algebra Subprograms) are routines that
       provide standard building blocks for performing basic vector and
       matrix operations."""

    homepage = "http://www.netlib.org/blas/_cblas/"

    # tarball has no version, but on the date below, this MD5 was correct.
    version('2015-06-06', '1e8830f622d2112239a4a8a83b84209a',
            url='http://www.netlib.org/blas/blast-forum/cblas.tgz')

    provides('cblas')

    depends_on('blas')
    parallel = False

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-cblas."""
        module.cblaslibname=[os.path.join(self.spec.prefix.lib, "libcblas.a")]

    def install(self, spec, prefix):
        blas_libs = " ".join(blaslibname)
        mf = FileFilter('Makefile.in')

        mf.filter('^BLLIB =.*', 'BLLIB = %s' % blas_libs)
        mf.filter('^CC =.*', 'CC = cc')
        mf.filter('^FC =.*', 'FC = f90')
        mf.filter('^CFLAGS =', 'CFLAGS = -fPIC ')
        mf.filter('^FFLAGS =', 'FFLAGS = -fPIC ')

        make('all')
        mkdirp(prefix.lib)
        mkdirp(prefix.include)

        # Rename the generated lib file to libcblas.a
        install('./lib/cblas_LINUX.a', '%s/libcblas.a' % prefix.lib)
        install('./include/cblas.h','%s' % prefix.include)
        install('./include/cblas_f77.h','%s' % prefix.include)
