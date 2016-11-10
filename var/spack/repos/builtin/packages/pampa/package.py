from spack import *
import os
import getpass
import spack

class Pampa(Package):
    """PaMPA is a middleware that manages distributed meshes. It allows
       users to write parallel solver codes without having to bother about
       data exchange, data redistribution, remeshing and load balancing.

       The release 1.0.0 requires to set the "PAMPA_TARBALL_100"
       environment variable to the absolute path of the PaMPA tarball,
       e.g. /home/doe/pampa-1.0.0.tar.gz. To use the SVN HEAD state,
       the user must have access to Pampa's repository on gforge.
       PLEASE MAKE SURE YOUR USERNAME MATCHES YOUR GFORGE ACCOUNT NAME
       OR SET SHELL VAR "GFORGE_USERNAME" TO YOUR GFORGE ACCOUNT NAME"""

    homepage = "http://gforge.inria.fr/projects/pampa-p/"

    try:
        repo=os.environ['PAMPA_TARBALL_100']
        version('1.0.0',
                '15d50fe872d7ab862988481764323167',
                url='file://'+repo, preferred=True)
    except KeyError:
        pass

    try:
        username = os.environ['GFORGE_USERNAME']
    except KeyError:
        username = getpass.getuser()
    version('trunk', svn='https://scm.gforge.inria.fr/authscm/' + username + '/svn/pampa-p/trunk')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('idx64', default=False, description='to use 64 bits integers')

    depends_on('cmake')
    depends_on('mpi')
    depends_on('scotch +mpi')
    depends_on('scotch +mpi +idx64', when='+idx64')
    depends_on('scotch@6.0.4 +mpi', when='@1.0.0')
    depends_on('scotch@6.0.4 +mpi +idx64', when='@1.0.0+idx64')

    def install(self, spec, prefix):
        with working_dir('spack-build', create=True):

            # configure
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DCMAKE_BUILD_TYPE=Release"])
            cmake_args.extend(["-DCOMM_TYPE=Point-to-point"])
            cmake_args.extend(["-DPTHREAD=None"])
            cmake_args.extend(["-DPAMPA_MULTILEVEL=True"])
            if spec.satisfies('+idx64'):
                cmake_args.extend(["-DINT_SIZE=64bits"])
            cmake(*cmake_args)

            # build
            make()

            #install
            make("install")

    # to use the existing version available in the environment: PAMPA_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('PAMPA_DIR'):
            pamparoot=os.environ['PAMPA_DIR']
            if os.path.isdir(pamparoot):
                os.symlink(pamparoot+"/bin", prefix.bin)
                os.symlink(pamparoot+"/include", prefix.include)
                os.symlink(pamparoot+"/lib", prefix.lib)
            else:
                raise RuntimeError(pamparoot+' directory does not exist.'+' Do you really have openmpi installed in '+pamparoot+' ?')
        else:
            raise RuntimeError('PAMPA_DIR is not set, you must set this environment variable to the installation path of your pampa')
