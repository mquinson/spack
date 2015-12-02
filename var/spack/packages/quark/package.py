from spack import *

class Quark(Package):
    """Enables the dynamic execution of tasks with data dependencies in a multi-core, multi-socket, shared-memory environment."""
    homepage = "http://icl.cs.utk.edu/quark/index.html"
    url      = "http://icl.cs.utk.edu/projectsfiles/quark/pubs/quark-0.9.0.tgz"

    version('0.9.0', '52066a24b21c390d2f4fb3b57e976d08')

    variant('debug', default=False, description='Enable debug symbols')

    depends_on("hwloc")

    def install(self, spec, prefix):
        mf = FileFilter('make.inc')
        mf.filter('prefix=./install', 'prefix=%s' % prefix)
        if spec.satisfies('+debug'):
            mf.filter('^CFLAGS=.*', 'CFLAGS=-g')

        make()
        make("install")
