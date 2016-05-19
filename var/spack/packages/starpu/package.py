from spack import *
import subprocess
import os
import platform
import spack

class Starpu(Package):
    """offers support for heterogeneous multicore architecture"""
    homepage = "http://starpu.gforge.inria.fr/"

    # Install from sources
    if os.environ.has_key("SPACK_STARPU_TAR"):
        version('custom', '9509fa4cd2790bc51b164103f2c87f3c', url = "file://%s" % os.environ['SPACK_STARPU_TAR'])
    else:
        version('1.2.0rc5', '5ee228354d0575c53e631ed359054cfd',
                url="http://starpu.gforge.inria.fr/files/starpu-1.2.0rc5.tar.gz")
        version('1.2.0rc4', '9509fa4cd2790bc51b164103f2c87f3c',
                url="http://starpu.gforge.inria.fr/files/starpu-1.2.0rc4.tar.gz")
        version('1.1.5', '88de3bceece7e22260edd0a37d28ae08',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.5.tar.gz")
        version('1.1.4', '1ba56a7a6deee19fd88c90920f9403cc',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.4.tar.gz")
        version('1.1.3', '97848eceee4926eb158e27ecb9365380',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.3.tar.gz")
        version('1.1.2', '985cb616910f8debff22be2c0e7699fa',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.2.tar.gz")
        version('1.1.1', 'd2dd09220cd47af50b585278ed5d7e01',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.1.tar.gz")
        version('1.1.0', '60a74f3ea6b3c6cd89ffa2b759d95bef',
                url="http://starpu.gforge.inria.fr/files/starpu-1.1.0.tar.gz")
        version('1.0.5', 'f7cc2ec26d595fd9d1df5bf856f56927',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.5.tar.gz")
        version('1.0.4', '3954c0675ead43398cadb73cbcffd8e4',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.4.tar.gz")
        version('1.0.3', '4aed2fe16057fbefafe9902c73ad56a7',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.3.tar.gz")
        version('1.0.2', '5105ffbeb1d88658663ea2e7d5865231',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.2.tar.gz")
        version('1.0.1', '72e9d92057f2b88483c27aca78c53316',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.1.tar.gz")
        version('1.0.0', '34177fa00fcff9f75b7650b307276b07',
                url="http://starpu.gforge.inria.fr/files/starpu-1.0.0.tar.gz")
        version('0.9.2', '51f9c5c19523e61e3e035bad3099b173',
                url="http://starpu.gforge.inria.fr/files/starpu-0.9.2.tar.gz")
        version('0.9.1', '675a22afdc68250bca2d8600cd73ee1b',
                url="http://starpu.gforge.inria.fr/files/starpu-0.9.1.tar.gz")
        version('0.9'  , 'bc69ab1d1a506b4e7f994b5fabbeaee7',
                url="http://starpu.gforge.inria.fr/files/starpu-0.9.tar.gz")
        version('0.4'  , '372a435987ff343e68088c6339068506',
                url="http://starpu.gforge.inria.fr/files/starpu-0.4.tar.gz")
        version('0.2'  , '763c9b1347026e035a25ed3709fec4fd',
                url="http://starpu.gforge.inria.fr/files/starpu-0.2.tar.gz")
        version('0.1'  , '658c7a8a3ef53599fd197ab3c7127c20',
                url="http://starpu.gforge.inria.fr/files/starpu-0.1.tar.gz")

    version('git-1.2', git='https://bitbucket.org/jeromerobert/starpu.git/starpu.git', branch='agi/cc-linux-dev')
    version('svn-trunk', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/trunk')
    version('svn-1.1', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/branches/starpu-1.1')
    version('svn-1.2', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/branches/starpu-1.2')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('debug', default=False, description='Enable debug symbols')
    variant('shared', default=True, description='Build STARPU as a shared library')
    variant('fxt', default=False, description='Enable FxT tracing support')
    variant('mpi', default=False, description='Enable MPI support')
    variant('cuda', default=False, description='Enable CUDA support')
    variant('opencl', default=False, description='Enable OpenCL support')
    variant('openmp', default=False, description='Enable OpenMP support')
    variant('simgrid', default=False, description='Enable SimGrid support')
    variant('examples', default=True, description='Enable Examples')
    variant('blas', default=False, description='Enable BLAS related features')

    depends_on("hwloc")
    depends_on("mpi", when='+mpi')
    depends_on("cuda", when='+cuda')
    depends_on("fxt", when='+fxt')
    depends_on("simgrid", when='+simgrid')
    depends_on("blas", when='+blas')

    def install(self, spec, prefix):

        if os.path.isfile("./autogen.sh"):
            subprocess.check_call("./autogen.sh")

        config_args = ["--prefix=" + prefix]
        config_args.append("--disable-build-doc")
        config_args.append("--disable-starpu-top")

        if spec.satisfies('+debug'):
            config_args.append("--enable-debug")

        if not spec.satisfies('+shared'):
            config_args.append("--disable-shared")

        if not spec.satisfies('+examples'):
            config_args.append("--disable-build-examples")

        if spec.satisfies('+fxt'):
            fxt = spec['fxt'].prefix
            config_args.append("--with-fxt=%s" % fxt)
            if spec.satisfies('@1.2:') or spec.satisfies('@svn-1.2') or spec.satisfies('@svn-trunk'):
                config_args.append("--enable-paje-codelet-details")

        if spec.satisfies('+simgrid'):
            simgrid = spec['simgrid'].prefix
            config_args.append("--enable-simgrid")
            config_args.append("--with-simgrid-dir=%s" % simgrid)
            if spec.satisfies('+mpi'):
                config_args.append("--with-mpicc=%s/bin/smpicc" % simgrid)

        if not spec.satisfies('+mpi'):
            config_args.append("--without-mpicc")

        if not spec.satisfies('+cuda'):
            config_args.append("--disable-cuda")

        if not spec.satisfies('+opencl'):
            config_args.append("--disable-opencl")

        if spec.satisfies('+openmp'):
            config_args.append("--enable-openmp=yes")
        else:
            config_args.append("--enable-openmp=no")

        configure(*config_args)

        # On OSX, deactivate glpk
        if platform.system() == 'Darwin':
            filter_file('^#define.*GLPK.*', '', 'src/common/config.h', 'include/starpu_config.h')

        make()
        make("install", parallel=False)

    # to use the existing version available in the environment: STARPU_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('STARPU_DIR'):
            starpuroot=os.environ['STARPU_DIR']
            if os.path.isdir(starpuroot):
                os.symlink(starpuroot+"/bin", prefix.bin)
                os.symlink(starpuroot+"/include", prefix.include)
                os.symlink(starpuroot+"/lib", prefix.lib)
            else:
                sys.exit(starpuroot+' directory does not exist.'+' Do you really have openmpi installed in '+starpuroot+' ?')
        else:
            sys.exit('STARPU_DIR is not set, you must set this environment variable to the installation path of your starpu')
