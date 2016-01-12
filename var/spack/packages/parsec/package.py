from spack import *
import spack

class Parsec(Package):
    """Parallel Runtime Scheduling and Execution Controller."""
    homepage = "http://icl.cs.utk.edu/parsec/index.html"

    version('last-rel', '3c09cc8bd413a435254d6cc0e2e5f663',
            url='http://icl.cs.utk.edu/projectsfiles/parsec/pubs/parsec-b9861d3a818f.tgz')

    pkg_dir = spack.db.dirname_for_package_name("parsec")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    depends_on("cmake")
    depends_on("hwloc")
    depends_on("mpi")
    depends_on("papi")

    def install(self, spec, prefix):
        cmake_args = ["-DBUILD_SHARED_LIBS=ON"]
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
                sys.exit(parsecroot+' directory does not exist.'+' Do you really have openmpi installed in '+parsecroot+' ?')
        else:
            sys.exit('PARSEC_DIR is not set, you must set this environment variable to the installation path of your parsec')
