from spack import *
import subprocess
import os
import platform
import spack

class Starpu(Package):
    """offers support for heterogeneous multicore architecture"""
    homepage = "http://starpu.gforge.inria.fr/"

    version('1.2.1', '9f04db940cfebb737241c4d4b2adcc92',
            url="http://starpu.gforge.inria.fr/files/starpu-1.2.1/starpu-1.2.1.tar.gz")
    version('1.2.0', '0cc98ac39b9cb4083c6c51399029d33b',
            url="http://starpu.gforge.inria.fr/files/starpu-1.2.0/starpu-1.2.0.tar.gz")
    version('1.1.6', '005a3c15b25cb36df09e2492035b5aad',
            url="http://starpu.gforge.inria.fr/files/starpu-1.1.6/starpu-1.1.6.tar.gz")

    version('git-1.2', git='https://bitbucket.org/jeromerobert/starpu.git/starpu.git', branch='agi/cc-linux-dev')
    version('svn-trunk', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/trunk')
    version('svn-1.1', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/branches/starpu-1.1')
    version('svn-1.2', svn='https://scm.gforge.inria.fr/anonscm/svn/starpu/branches/starpu-1.2')

    variant('shared', default=True, description='Build STARPU as a shared library')
    variant('fast', default=True, description='Disable runtime assertions')
    variant('verbose', default=True, description='Enable verbose debugging')
    variant('fxt', default=False, description='Enable FxT tracing support')
    variant('mpi', default=True, description='Enable MPI support')
    variant('cuda', default=False, description='Enable CUDA support')
    variant('opencl', default=False, description='Enable OpenCL support')
    variant('openmp', default=True, description='Enable OpenMP support')
    variant('fortran', default=False, description='Enable Fortran interface and examples')
    variant('simgrid', default=False, description='Enable SimGrid support')
    variant('simgrid-mc', default=False, description='Enable SimGrid model checker support')
    variant('examples', default=True, description='Enable Examples')
    variant('blas', default=False, description='Enable BLAS related features')
    variant('mlr', default=True, description='Enable multiple linear regression models')

    depends_on("hwloc")
    depends_on("hwloc+cuda", when='+cuda')
    depends_on("mpi", when='+mpi~simgrid')
    depends_on("cuda", when='+cuda~simgrid')
    depends_on("fxt", when='+fxt')
    depends_on("simgrid", when='+simgrid')
    depends_on("simgrid+smpi", when='+simgrid+mpi')
    depends_on("simgrid+mc", when='+simgrid+mc')
    depends_on("blas", when='+blas')

    def install(self, spec, prefix):

        if not os.path.isfile("./configure"):
            if os.path.isfile("./autogen.sh"):
                subprocess.call(['libtoolize', '--copy', '--force'], shell=False)
                subprocess.check_call("./autogen.sh")
            else:
                raise RuntimeError('Neither configure nor autogen.sh script exist. StarPU Cannot configure.')

        # add missing lib for simgrid static compilation, already fixed since StarPU 1.2.1
        if spec.satisfies('+fxt'):
            mf = FileFilter('configure')
            mf.filter('libfxt.a -lrt', 'libfxt.a -lrt -lbfd')

        config_args = ["--prefix=" + prefix]
        config_args.append("--disable-build-doc")
        config_args.append("--disable-starpu-top")

        if spec.satisfies('+debug'):
            config_args.append("--enable-debug")

        if spec.satisfies('+verbose'):
            config_args.append("--enable-verbose")

        if not spec.satisfies('+shared'):
            config_args.append("--disable-shared")

        if not spec.satisfies('+fast'):
            config_args.append("--enable-fast")

        if not spec.satisfies('+examples'):
            config_args.append("--disable-build-examples")
            config_args.append("--disable-build-tests")

        if spec.satisfies('+fxt'):
            fxt = spec['fxt'].prefix
            config_args.append("--with-fxt=%s" % fxt)
            if spec.satisfies('@1.2:') or spec.satisfies('@svn-1.2') or spec.satisfies('@svn-trunk') or spec.satisfies('@git-1.2'):
                config_args.append("--enable-paje-codelet-details")

        if spec.satisfies('+simgrid'):
            simgrid = spec['simgrid'].prefix
            config_args.append("--enable-simgrid")
            config_args.append("--with-simgrid-dir=%s" % simgrid)
            if spec.satisfies('+mpi'):
                config_args.append("--with-mpicc=%s/bin/smpicc" % simgrid)
            if spec.satisfies('+sigmrid-mc'):
                config_args.append("--enable-simgrid-mc")

        config_args.append("--with-hwloc=%s" % spec['hwloc'].prefix)

        if not spec.satisfies('+mpi'):
            config_args.append("--without-mpicc")

        if not spec.satisfies('+cuda') or spec.satisfies('+simgrid'):
            config_args.append("--disable-cuda")
        else:
            config_args.append("--enable-cuda")

        if not spec.satisfies('+opencl'):
            config_args.append("--disable-opencl")

        if spec.satisfies('+openmp'):
            config_args.append("--enable-openmp=yes")
        else:
            config_args.append("--enable-openmp=no")

        if not spec.satisfies('+fortran'):
            config_args.append("--disable-fortran")

        if spec.satisfies('@svn-trunk'):
            if spec.satisfies('~mlr'):
                config_args.append("--disable-mlr")

        configure(*config_args)

        # On OSX, deactivate glpk
        if platform.system() == 'Darwin':
            filter_file('^#define.*GLPK.*', '', 'src/common/config.h', 'include/starpu_config.h')

        make()
        make("install", parallel=False)
