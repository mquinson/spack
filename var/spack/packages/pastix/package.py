from spack import *
import os

class Pastix(Package):
    """a high performance parallel solver for very large sparse linear systems based on direct methods"""
    homepage = "http://pastix.gforge.inria.fr/files/README-txt.html"
#    url      = "https://gforge.inria.fr/frs/download.php/file/34392/pastix_5.2.2.20.tar.bz2"

    version('local', 'b7b158c5014cfff19d942017e309833a',
            url='file:///home/pruvost/work/archives/pastix.tar.gz')

    variant('mpi', default=False, description='Enable MPI')
    variant('cuda', default=False, description='Enable CUDA kernels. Caution: only available if StarPU variant is enabled')
    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')
    variant('metis', default=False, description='Enable Metis')
    variant('scotch', default=False, description='Enable Scotch')
    variant('starpu', default=False, description='Enable StarPU')

    depends_on("hwloc")
    depends_on("mpi", when='+mpi')
    depends_on("blas", when='~mkl')
    depends_on("scotch", when='+scotch')
    depends_on("metis", when='+metis')
    depends_on("starpu", when='+starpu')

    def install(self, spec, prefix):

        with working_dir('src'):

            with working_dir('spack-build', create=True):

                cmake_args = [
                    "..",
                    "-DBUILD_SHARED_LIBS=ON"]

                if '+mpi' in spec:
                    # Enable MPI here.
                    cmake_args.extend(["-DPASTIX_WITH_MPI=ON"])
                else:
                    # Disable MPI here.
                    cmake_args.extend(["-DPASTIX_WITH_MPI=OFF"])
                if '+metis' in spec:
                    # Enable Metis here.
                    cmake_args.extend(["-DPASTIX_ORDERING_METIS=ON"])
                else:
                    # Disable Metis here.
                    cmake_args.extend(["-DPASTIX_ORDERING_METIS=OFF"])
                if '+scotch' in spec:
                    # Enable Scotch here.
                    cmake_args.extend(["-DPASTIX_ORDERING_SCOTCH=ON"])
                else:
                    # Disable Scotch here.
                    cmake_args.extend(["-DPASTIX_ORDERING_SCOTCH=OFF"])
                if '+starpu' in spec:
                    # Enable StarPU here.
                    cmake_args.extend(["-DPASTIX_WITH_STARPU=ON"])
                    if '+cuda' in spec:
                        # Enable CUDA here.
                        cmake_args.extend(["-DPASTIX_WITH_STARPU_CUDA=ON"])
                    else:
                        # Disable CUDA here.
                        cmake_args.extend(["-DPASTIX_WITH_STARPU_CUDA=OFF"])
                else:
                    # Disable StarPU here.
                        cmake_args.extend(["-DPASTIX_WITH_STARPU=OFF"])

                if '+mkl' not in spec:
                    blas = self.spec['blas']
                    cmake_args.extend(['-DBLAS_DIR=%s' % blas.prefix])
                    if "%gcc" in spec:
                        os.environ["LDFLAGS"] = "-lgfortran"

                cmake_args.extend(std_cmake_args)

                cmake(*cmake_args)
                make()
                make("install")
