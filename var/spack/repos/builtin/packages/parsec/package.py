from spack import *
import spack

class Parsec(Package):
    """Parallel Runtime Scheduling and Execution Controller."""
    homepage = "http://icl.cs.utk.edu/parsec/index.html"

    version('last-rel', '3c09cc8bd413a435254d6cc0e2e5f663',
            url='http://icl.cs.utk.edu/projectsfiles/parsec/pubs/parsec-b9861d3a818f.tgz')
    version ('master', git='https://bitbucket.org/icldistcomp/parsec.git', branch='master')
    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('mpi', default=True, description='Enable MPI support')
    variant('papi', default=False, description='Enable PAPI support for using PINS')
    variant('shared', default=False, description='Enable shared library')
    variant('idx64', default=False, description='Enable 64bits')
    variant('dplasma', default=False, description='Enable DPlasma')

    depends_on("cmake")
    depends_on("hwloc")
    depends_on("mpi", when="+mpi")
    depends_on("papi", when="+papi")

    def install(self, spec, prefix):

        if spec.satisfies('+shared'):
            cmake_args = ["-DBUILD_SHARED_LIBS=ON"]
        else:
            cmake_args = ["-DBUILD_SHARED_LIBS=OFF"]

        if spec.satisfies('+idx64'):
            cmake_args = ["-DBUILD_64bits=ON"]
        else:
            cmake_args = ["-DBUILD_64bits=OFF"]

        if spec.satisfies('+dplasma'):
            cmake_args = ["-DBUILD_DPLASMA=ON"]
        else:
            cmake_args = ["-DBUILD_DPLASMA=OFF"]

        cmake.args = ['-DDAGUE_WITH_DEVEL_HEADERS=ON']
        cmake_args.extend(std_cmake_args)
        cmake(*cmake_args)
        make()
        make("install")

    # to use the existing version available in the environment: PARSEC_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('PARSEC_DIR'):
            parsecroot=os.environ['PARSEC_DIR']
            if os.path.isdir(parsecroot):
                os.symlink(parsecroot+"/bin", prefix.bin)
                os.symlink(parsecroot+"/include", prefix.include)
                os.symlink(parsecroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(parsecroot+' directory does not exist.'+' Do you really have openmpi installed in '+parsecroot+' ?')
        else:
            raise RuntimeError('PARSEC_DIR is not set, you must set this environment variable to the installation path of your parsec')
