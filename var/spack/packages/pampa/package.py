from spack import *
import getpass

class Pampa(Package):
    """PaMPA is a middleware that manages distributed meshes. It allows
       users to write parallel solver codes without having to bother about
       data exchange, data redistribution, remeshing and load balancing"""

    homepage = "http://gforge.inria.fr/projects/pampa-p/"
    url      = "http://www.example.com/pampa-1.0.tar.gz"

    version('svn-head', svn='https://scm.gforge.inria.fr/authscm/'+getpass.getuser()+'/svn/pampa-p/trunk')

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
