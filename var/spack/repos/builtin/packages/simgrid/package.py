from spack import *
import os
import spack

class Simgrid(Package):
    """To study the behavior of large-scale distributed systems such as Grids, Clouds, HPC or P2P systems."""
    homepage = "http://simgrid.org/"
    url      = "https://gforge.inria.fr/frs/download.php/file/37294/SimGrid-3.18.tar.gz"


    version('3.18', 'a3f457f70eb9ef095c275672b21247f4',
            url='https://gforge.inria.fr/frs/download.php/file/37294/SimGrid-3.18.tar.gz')
    version('3.13', '8ace1684972a01429d5f1c5db8966709',
            url='http://gforge.inria.fr/frs/download.php/file/35817/SimGrid-3.13.tar.gz')
    version('3.12', 'd73faaf81d7a9eb0d309cfd72532c5f1',
            url='http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz')
    version('3.11', '358ed81042bd283348604eb1beb80224',
            url='http://gforge.inria.fr/frs/download.php/file/33683/SimGrid-3.11.tar.gz')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git')
    version('starpumpi', git='https://scm.gforge.inria.fr/anonscm/git/simgrid/simgrid.git', branch='starpumpi')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('doc', default=False, description='Enable building documentation')
    variant('smpi', default=True, description='SMPI provides MPI')
    variant('examples', default=False, description='Install examples')

    depends_on('cmake')

    def build(self, spec, prefix):
        make()
        make("install")

    def setup_dependent_package(self, module, dep_spec):
        if self.spec.satisfies('+smpi'):
            self.spec.smpicc  = join_path(self.prefix.bin, 'smpicc')
            self.spec.smpicxx = join_path(self.prefix.bin, 'smpicxx -std=c++11')
            self.spec.smpifc  = join_path(self.prefix.bin, 'smpif90')
            self.spec.smpif77 = join_path(self.prefix.bin, 'smpiff')

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
