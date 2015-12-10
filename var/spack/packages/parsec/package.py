from spack import *

class Parsec(Package):
    """Parallel Runtime Scheduling and Execution Controller."""
    homepage = "http://icl.cs.utk.edu/parsec/index.html"

    version('last-rel', '3c09cc8bd413a435254d6cc0e2e5f663',
            url='http://icl.cs.utk.edu/projectsfiles/parsec/pubs/parsec-b9861d3a818f.tgz')

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
