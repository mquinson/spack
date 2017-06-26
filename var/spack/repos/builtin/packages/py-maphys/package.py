import shutil
import os
from spack import *


class PyMaphys(Package):
    """Description"""

    url = "https://gitlab.inria.fr/gmarait/PYMAPHYS"
    gitlink = "https://gitlab.inria.fr/gmarait/PYMAPHYS.git"

    version('master', git=gitlink, branch='master')

    depends_on("maphys+shared")
    depends_on("python")
    depends_on("py-mpi4py")
    depends_on("py-numpy")
    depends_on("py-scipy")
    depends_on("swig")

    pypath = ''

    def install(self, spec, prefix):
        for d in ["lib", "examples"]:
            target = os.path.join(prefix, d)
            shutil.copytree(d, target)
        shutil.copy("README.org", prefix)

    def setup_environment(self, spack_env, run_env):
        pypath = os.path.join(self.prefix, 'lib')
        run_env.prepend_path('PYTHONPATH', pypath)
