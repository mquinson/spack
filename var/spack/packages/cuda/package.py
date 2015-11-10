from spack import *
import os
import spack
import sys

class Cuda(Package):
    """Nvidia CUDA/cuBLAS routines"""
    homepage = "https://developer.nvidia.com/cuda-zone"

    pkg_dir = spack.db.dirname_for_package_name("cuda")

    # fake tarball because we consider it is already installed
    version('0.1.0', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        if os.getenv('CUDA_ROOT'):
            cudaroot=os.environ['CUDA_ROOT']
            if os.path.isdir(cudaroot):
                os.symlink(cudaroot+"/bin", prefix.bin)
                os.symlink(cudaroot+"/include", prefix.include)
                os.symlink(cudaroot+"/lib64", prefix.lib)
            else:
                sys.exit(cudaroot+' directory does not exist.'+' Do you really have Nvidia CUDA installed in '+cudaroot+' ?')
        else:
            sys.exit('CUDA_ROOT environment variable does not exist. Please set CUDA_ROOT to use Nvidia CUDA')
