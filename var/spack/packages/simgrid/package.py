from spack import *
import os
import spack

class Simgrid(Package):
    """To study the behavior of large-scale distributed systems such as Grids, Clouds, HPC or P2P systems."""
    homepage = "http://simgrid.gforge.inria.fr/index.html"
    url      = "http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz"

    # Install from sources
    if os.environ.has_key("SPACK_SIMGRID_TAR"):
        version('custom', 'd73faaf81d7a9eb0d309cfd72532c5f1', url = "file://%s" % os.environ['SPACK_SIMGRID_TAR'])
    else:
        version('3.12', 'd73faaf81d7a9eb0d309cfd72532c5f1',
                url='http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz')
        version('3.11', '358ed81042bd283348604eb1beb80224',
                url='http://gforge.inria.fr/frs/download.php/file/33683/SimGrid-3.11.tar.gz')
        version('3.10', 'a345ad07e37539d54390f817b7271de7',
                url='http://gforge.inria.fr/frs/download.php/file/33124/SimGrid-3.10.tar.gz')
        version('master', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git')
        version('starpumpi', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git', branch='starpumpi')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('doc', default=False, description='Enable building documentation')
    variant('smpi', default=True, description='SMPI provides MPI')
    variant('examples', default=False, description='Install examples')

    depends_on('cmake')

    provides('mpi@simu', when='+smpi')

    def build(self, spec, prefix):
        make()
        make("install")

    def setup_dependent_environment(self, module, spec, dep_spec):
        if spec.satisfies('+smpi'):
            bin = self.prefix.bin
            module.binmpicc  = os.path.join(bin, 'smpicc')
            module.binmpicxx = os.path.join(bin, 'smpicxx -std=c++11')
            module.binmpif77 = os.path.join(bin, 'smpiff')
            module.binmpif90 = os.path.join(bin, 'smpif90')

    def install(self, spec, prefix):
        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        if not spec.satisfies('+doc'):
            cmake_args.extend(["-Denable_documentation=OFF"])
        cmake(*cmake_args)
        self.build(spec,prefix)
        if spec.satisfies('+examples'):
            install_tree('examples', prefix + '/examples')

    # to use the existing version available in the environment: SIMGRID_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        install_tree("bin", prefix.bin)
        install_tree("include", prefix.include)
        install_tree("lib", prefix.lib)
        if spec.satisfies('+examples'):
            install_tree("examples", prefix + '/examples')
