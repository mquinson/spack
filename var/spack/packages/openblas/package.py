from spack import *
import os
import platform

class Openblas(Package):
    """An optimized BLAS library based on GotoBLAS2 1.13 BSD version."""
    homepage = "http://www.openblas.net/"
    url      = "http://github.com/xianyi/OpenBLAS/archive/v0.2.15.tar.gz"

    version('0.2.15', 'b1190f3d3471685f17cfd1ec1d252ac9')
    version('develop', git='https://github.com/xianyi/OpenBLAS.git', branch='develop')

    provides('blas')

    variant('mt', default=False, description="Use Multithreaded version")
    variant('openmp', default=False, description="Use Multithreaded version with OpenMP compatibility")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for netlib-blas."""
        if platform.system() == 'Darwin':
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libopenblas.dylib")]
        else:
            module.blaslibname=[os.path.join(self.spec.prefix.lib, "libopenblas.so")]
        if spec.satisfies('+mt'):
            module.blaslibname+=["-lpthread"]
        module.blaslibfortname = module.blaslibname

    def install(self, spec, prefix):

        # build
        if not spec.satisfies('+mt'):
            make('USE_THREAD=0', 'NO_LAPACK=1', 'NO_CBLAS=1', parallel=False)
        elif spec.satisfies('+openmp'):
            make('USE_OPENMP=1', 'NO_LAPACK=1', 'NO_CBLAS=1', parallel=False)
        else:
            make('NO_LAPACK=1', 'NO_CBLAS=1', parallel=False)

        # install
        make('install', 'PREFIX=%s' % prefix)
