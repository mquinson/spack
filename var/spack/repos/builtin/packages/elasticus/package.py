from spack import *
import os
import getpass
import spack

class Elasticus(Package):
    """Elasticus is a sequential library, to simulate wave propagation in
    geophysical environment based on a Discontinuous Glerkin method.

       As there is no publically released version of elasticus yet,
       this package requires the user has access to elasticus
       repository on gforge.  PLEASE MAKE SURE YOUR USERNAME MATCHES
       YOUR GFORGE ACCOUNT NAME OR SET SHELL VAR "GFORGE_USERNAME" TO
       YOUR GFORGE ACCOUNT NAME

    """

    homepage = "https://gforge.inria.fr/projects/wavepropaglib/"

    try:
        username = os.environ['GFORGE_USERNAME']
    except KeyError:
        username = getpass.getuser()

    version('master', git='https://' + username + '@scm.gforge.inria.fr/authscm/' + username + '/git/wavepropaglib/wavepropaglib.git')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    depends_on('cmake')
    depends_on('metis')
    depends_on('lapack')

    def install(self, spec, prefix):
        with working_dir('build', create=True):
            # configure
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])
            cmake(*cmake_args)

            # build
            make()

            #install
            make("install")

    # to use the existing version available in the environment: ELASTICUS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('ELASTICUS_DIR'):
            elasticusroot=os.environ['ELASTICUS_DIR']
            if os.path.isdir(elasticusroot):
                os.symlink(elasticusroot+"/bin", prefix.bin)
                os.symlink(elasticusroot+"/include", prefix.include)
                os.symlink(elasticusroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(elasticusroot+' directory does not exist.'+' Do you really have openmpi installed in '+elasticusroot+' ?')
        else:
            raise RuntimeError('ELASTICUS_DIR is not set, you must set this environment variable to the installation path of your elasticus')
