from spack import *

class PyGenfem(Package):
    """a fast and easy way to generate finite element matrices"""

    homepage = "https://gitlab.inria.fr/solverstack/genfem"
    url      = "https://gitlab.inria.fr/solverstack/genfem.git"

    version('git',  git='https://gitlab.inria.fr/solverstack/genfem.git')
    version('1.1',  git='https://gitlab.inria.fr/solverstack/genfem.git', tag="1.1", preferred=True)

    extends('python')

    depends_on('py-numpy')
    depends_on('py-scipy')
    depends_on('py-sympy')

    def install(self, spec, prefix):
        python('setup.py', 'install', '--prefix=%s' % prefix)
