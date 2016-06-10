from spack import *
import os
import spack
from shutil import copyfile

class Plasma(Package):
    """Parallel Linear Algebra for Scalable Multi-core Architectures."""
    homepage = "http://icl.cs.utk.edu/plasma/"

    version('2.8.0', 'd2e0c6f00a16efb9d79b54b99d89e1a6',
            url="http://icl.cs.utk.edu/projectsfiles/plasma/pubs/plasma_2.8.0.tar.gz")
    version('2.7.1', 'c3deb85ccf10e6eaac9f0ba663702805',
            url="http://icl.cs.utk.edu/projectsfiles/plasma/pubs/plasma_2.7.1.tar.gz")
    version('2.7.0', '8fcdfaf36832ab98e59b8299263999ca',
            url="http://icl.cs.utk.edu/projectsfiles/plasma/pubs/plasma_2.7.0.tar.gz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on("hwloc")
    depends_on("blas")
    depends_on("lapack")
    depends_on("cblas")
    depends_on("netlib-lapacke")

    def patch_core_blas_h(self):
        mf = FileFilter('include/core_blas.h')
        mf.filter('^#define CBLAS_TRANSPOSE enum CBLAS_TRANSPOSE', '')
        mf.filter('^#define CBLAS_UPLO      enum CBLAS_UPLO', '')
        mf.filter('^#define CBLAS_DIAG      enum CBLAS_DIAG', '')
        mf.filter('^#define CBLAS_SIDE      enum CBLAS_SIDE', '')

    def setup(self):
        copyfile('make.inc.example', 'make.inc')
        mf = FileFilter('make.inc')
        spec = self.spec

        mf.filter('^CC        =.*', 'prefix=%s\n\nCC        = cc' % self.prefix)
        mf.filter('^FC        =.*', 'FC        = f90')
        mf.filter('^LOADER    =.*', 'LOADER    = f90')

        # disable intel specific options
        if spec.satisfies('%gcc'):
            mf.filter('-nofor_main', '')
            mf.filter('-fltconsistency -fp_port', '')
            mf.filter('-diag-disable vec', '')

        if '^mkl' in spec:
            mf.filter('-O2 -DADD_', '-O2 -DADD_ -m64 -I${MKLROOT}/include')

        blas = spec['blas'].prefix
        blas_libs = spec['blas'].cc_link
        mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = %s' % blas_libs)

        cblas = spec['cblas'].prefix
        cblas_libs = spec['cblas'].cc_link
        mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = %s' % cblas_libs)

        lapack = spec['lapack'].prefix
        lapack_libs = spec['lapack'].cc_link
        mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = %s' % lapack_libs)

        lapacke = spec['netlib-lapacke'].prefix
        lapacke_libs = spec['netlib-lapacke'].cc_link
        mf.filter('^INCCLAPACK  =.*', 'INCCLAPACK  = -I%s' % lapacke.include)
        mf.filter('^LIBCLAPACK  =.*', 'LIBCLAPACK  = %s' % lapacke_libs)

    def install(self, spec, prefix):

        self.patch_core_blas_h()
        self.setup()
        make()
        make("install")
        # examples are not installed by default
        install_tree('testing', '%s/lib/plasma/testing' % prefix)
        install_tree('timing', '%s/lib/plasma/timing' % prefix)

    # to use the existing version available in the environment: PLASMA_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('PLASMA_DIR'):
            plasmaroot=os.environ['PLASMA_DIR']
            if os.path.isdir(plasmaroot):
                os.symlink(plasmaroot+"/bin", prefix.bin)
                os.symlink(plasmaroot+"/include", prefix.include)
                os.symlink(plasmaroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(plasmaroot+' directory does not exist.'+' Do you really have openmpi installed in '+plasmaroot+' ?')
        else:
            raise RuntimeError('PLASMA_DIR is not set, you must set this environment variable to the installation path of your plasma')
