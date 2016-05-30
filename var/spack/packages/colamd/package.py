from spack import *
from subprocess import call
import platform
import spack
from shutil import copyfile

class Colamd(Package):
    """approximate minimum degree column ordering"""
    homepage = "http://faculty.cse.tamu.edu/davis/suitesparse.html"

    version('4.4.6', '131a3a5e2dee784cd946284e44ce9af2',
            url = "http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.4.6.tar.gz")
    version('4.4.5', 'a2926c27f8a5285e4a10265cc68bbc18',
            url = "http://faculty.cse.tamu.edu/davis/SuiteSparse/SuiteSparse-4.4.5.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for colamd."""
        libdir = self.spec.prefix+"/lib"
        module.colamdlibname=["-L%s -lcolamd -lsuitesparseconfig" % libdir]
        if platform.system() == 'Linux':
            module.colamdlibname+=["-lrt"]

    def setup(self):
        spec = self.spec
        with working_dir('SuiteSparse_config'):
            if platform.system() == 'Darwin':
                copyfile('SuiteSparse_config_Mac.mk', 'SuiteSparse_config.mk')
            mf = FileFilter('SuiteSparse_config.mk')
            mf.filter('^INSTALL_LIB =.*', 'INSTALL_LIB = %s' % spec.prefix.lib)
            mf.filter('^INSTALL_INCLUDE =.*', 'INSTALL_INCLUDE = %s' % spec.prefix.include)
            if platform.system() == 'Darwin':
                mf.filter('  BLAS = -framework Accelerate', '')
                mf.filter('  LAPACK = -framework Accelerate', '')

    def install(self, spec, prefix):

        self.setup()
        mkdirp(prefix.include)
        mkdirp(prefix.lib)
        with working_dir('SuiteSparse_config'):
            make()
            make("install")
        with working_dir('COLAMD'):
            make()
            make("install")

    # to use the existing version available in the environment: COLAMD_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('COLAMD_DIR'):
            colamdroot=os.environ['COLAMD_DIR']
            if os.path.isdir(colamdroot):
                os.symlink(colamdroot+"/bin", prefix.bin)
                os.symlink(colamdroot+"/include", prefix.include)
                os.symlink(colamdroot+"/lib", prefix.lib)
            else:
                sys.exit(colamdroot+' directory does not exist.'+' Do you really have openmpi installed in '+colamdroot+' ?')
        else:
            sys.exit('COLAMD_DIR is not set, you must set this environment variable to the installation path of your colamd')
