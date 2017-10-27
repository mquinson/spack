import shutil
import os
from spack import *


class PyMaphys(Package):
    """Description"""

    homepage = "https://gitlab.inria.fr/gmarait/PYMAPHYS"
    url = "https://gitlab.inria.fr/gmarait/PYMAPHYS"
    gitlink = "https://gitlab.inria.fr/gmarait/PYMAPHYS.git"

    version('master', git=gitlink, branch='master')

    depends_on("maphys+shared")
    depends_on("python")
    depends_on("py-mpi4py")
    depends_on("py-numpy")
    depends_on("py-scipy")

    def install(self, spec, prefix):
        python('setup.py', 'install', '--prefix=%s' % prefix)
