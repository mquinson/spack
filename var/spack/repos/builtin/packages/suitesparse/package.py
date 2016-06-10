from spack import *
from subprocess import call
import platform
import spack
from shutil import copyfile

class Suitesparse(Package):
    """a suite of sparse matrix algorithms."""
    homepage = "http://faculty.cse.tamu.edu/davis/suitesparse.html"

    version('4.4.6', '131a3a5e2dee784cd946284e44ce9af2',
            url = "http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.4.6.tar.gz")
    version('4.4.5', 'a2926c27f8a5285e4a10265cc68bbc18',
            url = "http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.4.5.tar.gz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on("blas")
    depends_on("lapack")
    depends_on("metis@4.0.1:4.0.3")

    def setup(self):
        spec = self.spec
        with working_dir('SuiteSparse_config'):
            if platform.system() == 'Darwin':
                copyfile('SuiteSparse_config_Mac.mk', 'SuiteSparse_config.mk')
            mf = FileFilter('SuiteSparse_config.mk')
            mf.filter('^INSTALL_LIB =.*', 'INSTALL_LIB = %s' % spec.prefix.lib)
            mf.filter('^INSTALL_INCLUDE =.*', 'INSTALL_INCLUDE = %s' % spec.prefix.include)

            blas_libs = spec['blas'].fc_link
            mf.filter('  BLAS = -lopenblas', '#  BLAS = -lopenblas')
            mf.filter('# BLAS = -lblas -lgfortran', '  BLAS = %s' % blas_libs)

            lapack_libs = spec['lapack'].fc_link
            mf.filter('  LAPACK = -llapack', '  LAPACK = %s' % lapack_libs)

            if platform.system() == 'Darwin':
                mf.filter('  BLAS = -framework Accelerate', '')
                mf.filter('  LAPACK = -framework Accelerate', '')

            metis = spec['metis'].prefix
            metis_libs = spec['metis'].cc_link
            mf.filter('^METIS_PATH =.*', 'METIS_PATH = %s' % metis)
            mf.filter('^METIS =.*', 'METIS = %s' % metis_libs)

        with working_dir('CHOLMOD/Demo'):
            mf = FileFilter('Makefile')
            mf.filter('\( cd \$\(METIS_PATH\) && \$\(MAKE\) \)', '#( cd $(METIS_PATH) && $(MAKE) )')

    def install(self, spec, prefix):

        self.setup()
        make('library', parallel=False)
        mkdirp(prefix.include)
        mkdirp(prefix.lib)
        make("install")

    # to use the existing version available in the environment: SUITESPARSE_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('SUITESPARSE_DIR'):
            suitesparseroot=os.environ['SUITESPARSE_DIR']
            if os.path.isdir(suitesparseroot):
                os.symlink(suitesparseroot+"/bin", prefix.bin)
                os.symlink(suitesparseroot+"/include", prefix.include)
                os.symlink(suitesparseroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(suitesparseroot+' directory does not exist.'+' Do you really have openmpi installed in '+suitesparseroot+' ?')
        else:
            raise RuntimeError('SUITESPARSE_DIR is not set, you must set this environment variable to the installation path of your suitesparse')
