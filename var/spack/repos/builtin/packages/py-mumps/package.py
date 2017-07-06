import shutil
import os
from spack import *

class PyMumps(Package):
    """Description"""

    homepage = "https://gitlab.inria.fr/gmarait/PYMUMPS"
    url = "https://gitlab.inria.fr/gmarait/PYMUMPS"
    gitlink = "https://gitlab.inria.fr/gmarait/PYMUMPS.git"

    version('master', git=gitlink, branch='master')

    depends_on("mumps@5.0.2+shared")
    depends_on("python")
    depends_on("py-mpi4py")
    depends_on("py-numpy")
    depends_on("py-scipy")

    pypath = ''

    # Mumps dependencies
    # To load before the mumps libraries

    def install(self, spec, prefix):
        for d in ["lib", "examples"]:
            target = os.path.join(prefix, d)
            shutil.copytree(d, target)
        shutil.copy("README.org", prefix)

        # Write in the cache the path of the found libraries

        deps = {
            'scalapack': 'scalapack',
            'scotcherr' : 'scotch',
            'scotch' : 'scotch',
            'ptscotch' : 'scotch',
            'esmumps' : 'scotch',
            'parmetis' : 'parmetis',
            'pord' : 'mumps',
            'mumps_common' : 'mumps',
            'cmumps' : 'mumps',
            'dmumps' : 'mumps',
            'smumps' : 'mumps',
            'zmumps' : 'mumps',
        }

        cachefile = os.path.join(prefix, "lib", "pymumps", "libcache.py")
        with open(cachefile, 'w') as f:
            f.write(r"libs_cache = {" + "\n")
            for libname, package in deps.items():
                f.write('"' + libname + '" : "' + os.path.join(str(spec[package].prefix.lib), "lib" + libname + ".so") + '",\n')

            # Add blas
            if 'openblas' in spec:
                f.write('"blas" : "' + os.path.join(str(spec['openblas'].prefix.lib), "libopenblas.so") + '",\n')
            if 'mkl' in spec:
                f.write('"blas" : "' + os.path.join(str(spec['mkl'].prefix.lib), "libmkl.so") + '",\n')

            f.write("}\n")

    def setup_environment(self, spack_env, run_env):
        pypath = os.path.join(self.prefix, 'lib')
        run_env.prepend_path('PYTHONPATH', pypath)
