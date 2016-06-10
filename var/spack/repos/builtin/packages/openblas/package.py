from spack import *
import os
import platform
import spack

class Openblas(Package):
    """An optimized BLAS library based on GotoBLAS2 1.13 BSD version."""
    homepage = "http://www.openblas.net/"

    version('0.2.18', '805e7f660877d588ea7e3792cda2ee65',
            url="http://github.com/xianyi/OpenBLAS/archive/v0.2.18.tar.gz")
    version('develop', git='https://github.com/xianyi/OpenBLAS.git', branch='develop')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    provides('blas')

    variant('mt', default=False, description="Use Multithreaded version")
    variant('openmp', default=False, description="Use Multithreaded version with OpenMP compatibility")

    def install(self, spec, prefix):

        # configure
        if spec.satisfies('+mt'):
            thread=1
        else:
            thread=0
        if spec.satisfies('+openmp'):
            openmp=1
        else:
            openmp=0

        # build
        make('NO_LAPACK=1', 'NO_CBLAS=1', 'USE_THREAD=%s'%thread, 'USE_OPENMP=%s'%openmp)

        # install
        make('install', 'NO_LAPACK=1', 'NO_CBLAS=1', 'PREFIX=%s' % prefix)

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
                raise RuntimeError(openblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+openblasroot+' ?')
        else:
            raise RuntimeError('BLAS_DIR is not set, you must set this environment variable to the installation path of your openblas')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for openblas."""
        self.spec.cc_link="-L%s -lopenblas" % self.spec.prefix.lib
        if self.spec.satisfies('+mt'):
            self.spec.cc_link+=[" -lpthread"]
        self.spec.fc_link=self.spec.cc_link
        self.spec.cc_link_mt = self.spec.cc_link
        self.spec.fc_link_mt = self.spec.fc_link