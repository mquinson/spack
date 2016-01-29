from spack import *
import os
import platform
import spack

class NetlibCblas(Package):
    """The BLAS (Basic Linear Algebra Subprograms) are routines that
       provide standard building blocks for performing basic vector and
       matrix operations."""

    homepage = "http://www.netlib.org/blas/_cblas/"

    # tarball has no version, but on the date below, this MD5 was correct.
    version('2015-06-06', '1e8830f622d2112239a4a8a83b84209a',
            url='http://www.netlib.org/blas/blast-forum/cblas.tgz')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

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
        # Rename the generated lib file to libcblas
        mf.filter('^CBLIB =.*', 'CBLIB = ../lib/libcblas.a')

        if spec.satisfies('+shared'):
            mf.filter('^ARCH\s*=.*', 'ARCH=$(CC) $(BLLIB)')
            mf.filter('^ARCHFLAGS\s*=.*', 'ARCHFLAGS=-shared -o')
            mf.filter('^RANLIB\s*=.*', 'RANLIB=echo')
            mf.filter('^CCFLAGS\s*=', 'CCFLAGS = -fPIC ')
            mf.filter('^FFLAGS\s*=', 'FFLAGS = -fPIC ')
            mf.filter('\.a', ".dylib" if platform.system() == 'Darwin' else ".so")

    def install(self, spec, prefix):

        self.setup()
        make('all')
        mkdirp(prefix.lib)
        mkdirp(prefix.include)

        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
        else:
            libext=".a"

        install('./lib/libcblas%s' % libext, '%s' % prefix.lib)
        install('./include/cblas.h','%s' % prefix.include)
        install('./include/cblas_f77.h','%s' % prefix.include)

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
                sys.exit(netlibcblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+netlibcblasroot+' ?')
        else:
            sys.exit('CBLAS_DIR is not set, you must set this environment variable to the installation path of your netlib-cblas')
