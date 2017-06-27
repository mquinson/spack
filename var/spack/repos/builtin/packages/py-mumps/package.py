import shutil
import os
from spack import *

class PyMumps(Package):
    """Description"""

    homepage = "https://gitlab.inria.fr/gmarait/PYMUMPS"
    url = "https://gitlab.inria.fr/gmarait/PYMUMPS"
    gitlink = "https://gitlab.inria.fr/gmarait/PYMUMPS.git"

    version('master', git=gitlink, branch='master')

    depends_on("mumps+shared")
    depends_on("python")
    depends_on("py-mpi4py")
    depends_on("py-numpy")
    depends_on("py-scipy")

    pypath = ''

    def install(self, spec, prefix):
        for d in ["lib", "examples"]:
            target = os.path.join(prefix, d)
            shutil.copytree(d, target)
        shutil.copy("README.org", prefix)

    def setup_environment(self, spack_env, run_env):
        pypath = os.path.join(self.prefix, 'lib')
        run_env.prepend_path('PYTHONPATH', pypath)
