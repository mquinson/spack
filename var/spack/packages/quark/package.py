from spack import *
import spack

class Quark(Package):
    """Enables the dynamic execution of tasks with data dependencies in a multi-core, multi-socket, shared-memory environment."""
    homepage = "http://icl.cs.utk.edu/quark/index.html"
    url      = "http://icl.cs.utk.edu/projectsfiles/quark/pubs/quark-0.9.0.tgz"

    version('0.9.0', '52066a24b21c390d2f4fb3b57e976d08')

    pkg_dir = spack.db.dirname_for_package_name("quark")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    variant('debug', default=False, description='Enable debug symbols')

    depends_on("hwloc")

    def install(self, spec, prefix):
        mf = FileFilter('make.inc')
        mf.filter('prefix=./install', 'prefix=%s' % prefix)
        if spec.satisfies('+debug'):
            mf.filter('^CFLAGS=.*', 'CFLAGS=-g')

        make()
        make("install")

    # to use the existing version available in the environment: QUARK_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('QUARK_DIR'):
            quarkroot=os.environ['QUARK_DIR']
            if os.path.isdir(quarkroot):
                os.symlink(quarkroot+"/bin", prefix.bin)
                os.symlink(quarkroot+"/include", prefix.include)
                os.symlink(quarkroot+"/lib", prefix.lib)
            else:
                sys.exit(quarkroot+' directory does not exist.'+' Do you really have openmpi installed in '+quarkroot+' ?')
        else:
            sys.exit('QUARK_DIR is not set, you must set this environment variable to the installation path of your quark')
