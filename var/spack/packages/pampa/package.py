from spack import *
import os
import getpass

class Pampa(Package):
    """PaMPA is a middleware that manages distributed meshes. It allows
       users to write parallel solver codes without having to bother about
       data exchange, data redistribution, remeshing and load balancing.
       As there is not yet a public release of the project I need to connect
       to the svn repository using your gforge account - this is assumed to
       be the same as your shell's username, if this is not correct please
       set environment variable PAMPA_USERNAME to your gforge account name."""

    homepage = "http://gforge.inria.fr/projects/pampa-p/"
    url      = "http://www.example.com/pampa-1.0.tar.gz"

    try:
        username = os.environ['PAMPA_USERNAME']
    except KeyError:
        username = getpass.getuser()

    version('svn-head', svn='https://scm.gforge.inria.fr/authscm/' + username + '/svn/pampa-p/trunk')

    depends_on('mpi')
    depends_on('scotch@6.0.0:6.0.3 +mpi ~pthread')

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):
            cmake_args = [
                "..",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DCOMM_TYPE=Point-to-point",
                "-DPTHREAD=None"]
            cmake_args.extend(std_cmake_args)

            cmake(*cmake_args)
            make()
            make("install")
