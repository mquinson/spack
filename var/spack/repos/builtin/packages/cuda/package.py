from spack import *
import os
import spack
import sys

class Cuda(Package):
    """Nvidia CUDA/cuBLAS routines"""
    homepage = "https://developer.nvidia.com/cuda-zone"

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        if os.getenv('CUDA_DIR'):
            cudaroot=os.environ['CUDA_DIR']
            if os.path.isdir(cudaroot):
                os.symlink(cudaroot+"/bin", prefix.bin)
                os.symlink(cudaroot+"/include", prefix.include)
                if os.path.isdir(cudaroot+"/lib64"):
                    os.symlink(cudaroot+"/lib64", prefix.lib64)
                if os.path.isdir(cudaroot+"/lib"):
                    os.symlink(cudaroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(cudaroot+' directory does not exist.'+' Do you really have Nvidia CUDA installed in '+cudaroot+' ?')
        else:
            raise RuntimeError('CUDA_DIR environment variable does not exist. Please set CUDA_DIR to use Nvidia CUDA')

    def setup_dependent_environment(self, spack_env, run_env, dependent_spec):
        spack_env.set('CUDADIR', self.spec.prefix)