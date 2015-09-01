from spack import *
from subprocess import call

class Suitesparse(Package):
    """a suite of sparse matrix algorithms."""
    homepage = "http://faculty.cse.tamu.edu/davis/suitesparse.html"
    url      = "http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.4.5.tar.gz"

    version('4.4.5', 'a2926c27f8a5285e4a10265cc68bbc18')

    variant('mkl', default=False, description='Use BLAS/ScaLAPACK from the Intel MKL library')

    depends_on("blas",when='~mkl')
    depends_on("lapack",when='~mkl')
    depends_on("metis@4.0.1:4.0.3")

    def patch(self):
        spec = self.spec
        with working_dir('SuiteSparse_config'):
            mf = FileFilter('SuiteSparse_config.mk')
            mf.filter('^INSTALL_LIB =.*', 'INSTALL_LIB = %s' % spec.prefix.lib)
            mf.filter('^INSTALL_INCLUDE =.*', 'INSTALL_INCLUDE = %s' % spec.prefix.include)

            mf.filter('  BLAS = -lopenblas', '#  BLAS = -lopenblas')
            if spec.satisfies('~mkl'):
                blas = spec['blas'].prefix
                lapack = spec['lapack'].prefix
                mf.filter('# BLAS = -lblas -lgfortran', '  BLAS = -L%s -lblas -lgfortran' % blas.lib)
                mf.filter('  LAPACK = -llapack', '  LAPACK = -L%s -llapack' % lapack.lib)
            if spec.satisfies('+mkl'):
                mf.filter('^# BLAS = -Wl,--start-group \$\(MKLROOT\).*',
                          'BLAS = -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm')
                mf.filter('^  LAPACK =.*', '  LAPACK =')

            metis = spec['metis'].prefix
            mf.filter('^METIS_PATH =.*', 'METIS_PATH = %s' % metis)
            mf.filter('^METIS =.*', 'METIS = %s/libmetis.a' % metis.lib)

        with working_dir('CHOLMOD/Demo'):
            mf = FileFilter('Makefile')
            mf.filter('\( cd \$\(METIS_PATH\) && \$\(MAKE\) \)', '#( cd $(METIS_PATH) && $(MAKE) )')

    def install(self, spec, prefix):

        make(parallel=False)
        mkdirp(prefix.include)
        mkdirp(prefix.lib)
        make("install")
