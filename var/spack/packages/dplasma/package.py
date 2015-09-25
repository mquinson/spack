from spack import *

class Dplasma(Package):
    """Distributed Parallel Linear Algebra Software for Multicore Architectures"""
    homepage = "http://icl.utk.edu/dplasma/"
    url      = "http://icl.cs.utk.edu/projectsfiles/parsec/pubs/dplasma-1.2.1.tgz"

    version('1.2.1', '8b899ba331926997ea96fbc381e2b6cd')
    version('1.2.0', 'f40c36139b6a1b526d2505d1e0237748')
    version('1.1.0', '72e1eec916be379ddb9dcd45c7a4b593')

    variant('mpi', default=True, description='Enable MPI')
    variant('cuda', default=False, description='Enable CUDA')
    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('papi', default=False, description='Enable PAPI')

    depends_on("hwloc")
    depends_on("plasma")
    depends_on("mpi", when='+mpi')
    depends_on("papi", when='+papi')

    def install(self, spec, prefix):
        cmake('.', *std_cmake_args)

        make()
        make("install")
