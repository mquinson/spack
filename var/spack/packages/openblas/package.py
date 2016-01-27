from spack import *
import os
import platform
import spack

class Openblas(Package):
    """An optimized BLAS library based on GotoBLAS2 1.13 BSD version."""
    homepage = "http://www.openblas.net/"

    version('0.2.15', 'b1190f3d3471685f17cfd1ec1d252ac9',
            url="http://github.com/xianyi/OpenBLAS/archive/v0.2.15.tar.gz")
    version('develop', git='https://github.com/xianyi/OpenBLAS.git', branch='develop')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    provides('blas')

    variant('mt', default=False, description="Use Multithreaded version")
    variant('openmp', default=False, description="Use Multithreaded version with OpenMP compatibility")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for openblas."""
        if platform.system() == 'Darwin':
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libopenblas.dylib")]
        else:
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libopenblas.so")]
        if spec.satisfies('+mt'):
            module.blaslibname+=["-lpthread"]
        module.blaslibfortname = module.blaslibname

    def install(self, spec, prefix):

        # configure
        options='NO_LAPACK=1 NO_CBLAS=1'

        if not spec.satisfies('+mt'):
            options+=' USE_THREAD=0'

        if spec.satisfies('+openmp'):
            options+=' USE_OPENMP=1'

        # build
        make('%s'%options, parallel=False)

        # install
        make('install', 'PREFIX=%s' % prefix)

    # to use the existing version available in the environment: BLAS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BLAS_DIR'):
            openblasroot=os.environ['BLAS_DIR']
            if os.path.isdir(openblasroot):
                os.symlink(openblasroot+"/bin", prefix.bin)
                os.symlink(openblasroot+"/include", prefix.include)
                os.symlink(openblasroot+"/lib", prefix.lib)
            else:
                sys.exit(openblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+openblasroot+' ?')
        else:
            sys.exit('BLAS_DIR is not set, you must set this environment variable to the installation path of your openblas')
