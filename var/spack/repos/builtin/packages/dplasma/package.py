from spack import *
import os
import sys
import spack

class Dplasma(Package):
    """Distributed Parallel Linear Algebra Software for Multicore Architectures"""
    homepage = "http://icl.utk.edu/dplasma/"
    url      = "http://icl.cs.utk.edu/projectsfiles/parsec/pubs/dplasma-1.2.1.tgz"

    version('1.2.1', '8b899ba331926997ea96fbc381e2b6cd')
    version('1.2.0', 'f40c36139b6a1b526d2505d1e0237748')
    version('1.1.0', '72e1eec916be379ddb9dcd45c7a4b593')
    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('mpi', default=True, description='Enable MPI')
    variant('cuda', default=False, description='Enable CUDA')
    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('papi', default=False, description='Enable PAPI')

    depends_on("cmake")
    depends_on("hwloc")
    depends_on("plasma")
    depends_on("mpi", when='+mpi')
    depends_on("papi", when='+papi')

    def install(self, spec, prefix):
        cmake('.', *std_cmake_args)

        make()
        make("install")

    # to use the existing version available in the environment: DPLASMA_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('DPLASMA_DIR'):
            dpalsmaroot=os.environ['DPLASMA_DIR']
            if os.path.isdir(dpalsmaroot):
                os.symlink(dpalsmaroot+"/include", prefix.include)
                os.symlink(dpalsmaroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(dpalsmaroot+' directory does not exist.'+' Do you really have openmpi installed in '+dpalsmaroot+' ?')
        else:
            raise RuntimeError('DPLASMA_DIR is not set, you must set this environment variable to the installation path of your dpalsma')