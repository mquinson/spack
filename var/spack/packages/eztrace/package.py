from spack import *
import subprocess
import os

class Eztrace(Package):
    """a tool that aims at generating automatically execution trace from HPC."""
    homepage = "http://eztrace.gforge.inria.fr/"
    url      = "http://gforge.inria.fr/frs/download.php/file/34082/eztrace-1.0.6.tar.gz"

    version('1.0.6', 'd613ab7caf28d3ce61d5aad39b76f324')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/eztrace/eztrace.git', branch='master')

    variant('mpi', default=False, description='Enable MPI')
    variant('papi', default=False, description='Enable papi, a hardware counter software')
    variant('starpu', default=False, description='Enable StarPU')

    depends_on("mpi", when='+mpi')
    depends_on("papi", when='+papi')
    depends_on("starpu", when='+starpu')

    def install(self, spec, prefix):

        # execute bootstrap first (recursive autoreconf)
        subprocess.check_call('./bootstrap')

        config_args = ["--prefix=" + prefix]

        if '+mpi' in spec:
            config_args.append("--with-mpi=%s" % spec['mpi'].prefix)

        if '+papi' in spec:
            config_args.append("--with-papi=%s" % spec['papi'].prefix)

        if '+starpu' in spec:
            config_args.append("--with-starpu=%s" % spec['starpu'].prefix)

        configure(*config_args)
        make()
        make("install")
