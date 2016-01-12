from spack import *
import os
import spack

class Scalfmm(Package):
    """a software library to simulate N-body interactions using the Fast Multipole Method."""
    homepage = "http://scalfmm-public.gforge.inria.fr/doc/"
    url      = "https://gforge.inria.fr/frs/download.php/file/34672/SCALFMM-1.3-56.tar.gz"

    version('1.4-148', '666ba8fef226630a2c22df8f0f93ff9c')
    version('1.3-56', '666ba8fef226630a2c22df8f0f93ff9c')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/scalfmm-public/scalfmm-public.git')

    pkg_dir = spack.db.dirname_for_package_name("scalfmm")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    variant('sse', default=True, description='Enable SSE')
    #variant('blas', default=False, description='Enable BLAS')
    variant('fftw', default=False, description='Enable FFTW')
    variant('mpi', default=False, description='Enable MPI')
    variant('starpu', default=False, description='Enable StarPU')
    variant('debug', default=False, description='Enable debug symbols')

    depends_on("cmake")
    # Does not compile without blas!
    #depends_on("blas", when='+blas')
    depends_on("blas")
    depends_on("lapack")
    depends_on("fftw", when='+fftw')
    depends_on("starpu", when='+starpu')
    depends_on("mpi", when='+mpi')

    def install(self, spec, prefix):

        with working_dir('spack-build', create=True):

            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args+=["-DBUILD_SHARED_LIBS=ON"]

            if spec.satisfies('+debug'):
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])

            if spec.satisfies('~sse'):
                # Disable SSE  here.
                cmake_args.extend(["-DSCALFMM_USE_SSE=OFF"])

            cmake_args.extend(["-DSCALFMM_USE_BLAS=ON"])
            # if spec.satisfies('+blas'):
            #     # Enable BLAS here.
            #     cmake_args.extend(["-DSCALFMM_USE_BLAS=ON"])
            # else:
            #     # Disable BLAS here.
            #     cmake_args.extend(["-DSCALFMM_USE_BLAS=OFF"])

            if spec.satisfies('+fftw'):
                # Enable FFTW here.
                cmake_args.extend(["-DSCALFMM_USE_FFT=ON"])
            else:
                # Disable FFTW here.
                cmake_args.extend(["-DSCALFMM_USE_FFT=OFF"])

            if spec.satisfies('+starpu'):
                # Enable STARPU here.
                cmake_args.extend(["-DSCALFMM_USE_STARPU=ON"])
            else:
                # Disable STARPU here.
                cmake_args.extend(["-DSCALFMM_USE_STARPU=OFF"])

            if spec.satisfies('+mpi'):
                # Enable MPI here.
                cmake_args.extend(["-DSCALFMM_USE_MPI=ON"])
            else:
                # Disable MPI here.
                cmake_args.extend(["-DSCALFMM_USE_MPI=OFF"])

            blas = self.spec['blas']
            lapack = self.spec['lapack']
            cmake_args.extend(['-DBLAS_DIR=%s' % blas.prefix])
            cmake_args.extend(['-DLAPACK_DIR=%s' % lapack.prefix])
            if spec.satisfies('%gcc'):
                os.environ["LDFLAGS"] = "-lgfortran"

            cmake(*cmake_args)
            make()
            make("install")

    # to use the existing version available in the environment: SCALFMM_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('SCALFMM_DIR'):
            scalfmmroot=os.environ['SCALFMM_DIR']
            if os.path.isdir(scalfmmroot):
                os.symlink(scalfmmroot+"/bin", prefix.bin)
                os.symlink(scalfmmroot+"/include", prefix.include)
                os.symlink(scalfmmroot+"/lib", prefix.lib)
            else:
                sys.exit(scalfmmroot+' directory does not exist.'+' Do you really have openmpi installed in '+scalfmmroot+' ?')
        else:
            sys.exit('SCALFMM_DIR is not set, you must set this environment variable to the installation path of your scalfmm')
