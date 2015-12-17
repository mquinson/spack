from spack import *
import os
import getpass

class Pampa(Package):
    """PaMPA is a middleware that manages distributed meshes. It allows
       users to write parallel solver codes without having to bother about
       data exchange, data redistribution, remeshing and load balancing.

       As there is no publically released version of pampa yet, this package
       requires that the user has access to Pampa's repository on gforge.
          PLEASE MAKE SURE YOUR USERNAME MATCHES YOUR GFORGE ACCOUNT NAME 
          OR SET SHELL VAR "GFORGE_USERNAME" TO YOUR GFORGE ACCOUNT NAME"""

    homepage = "http://gforge.inria.fr/projects/pampa-p/"
    url      = "http://www.example.com/pampa-1.0.tar.gz"

    try:
        username = os.environ['PAMPA_USERNAME']
    except KeyError:
        username = getpass.getuser()

    version('svn-head', svn='https://scm.gforge.inria.fr/authscm/' + username + '/svn/pampa-p/trunk')

    depends_on('cmake')
    depends_on('mpi')
    depends_on('scotch@6.0.0:6.0.3 +mpi ~pthread')

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):

            # configure
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])
            cmake_args.extend(["-DCOMM_TYPE=Point-to-point"])
            cmake_args.extend(["-DPTHREAD=None"])
            cmake(*cmake_args)

            # build
            make()

            #install
            make("install")
