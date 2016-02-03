from spack import *
import subprocess
import os
import spack

class Eztrace(Package):
    """a tool that aims at generating automatically execution trace from HPC."""
    homepage = "http://eztrace.gforge.inria.fr/"
    url      = "http://gforge.inria.fr/frs/download.php/file/35111/eztrace-1.1.tar.gz"

    version('1.1-2', '0a034b14fe7fc0ea22cf044427e88f0f',
            url='https://gforge.inria.fr/frs/download.php/file/35458/eztrace-1.1-2.tar.gz')
    version('1.1', '678efede6c1b9f105a0b9e1c458f725d',
            url='http://gforge.inria.fr/frs/download.php/file/35111/eztrace-1.1.tar.gz')
    version('1.0.6', 'd613ab7caf28d3ce61d5aad39b76f324',
            url='http://gforge.inria.fr/frs/download.php/file/34082/eztrace-1.0.6.tar.gz')
    version('master', git='https://scm.gforge.inria.fr/anonscm/git/eztrace/eztrace.git', branch='master')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('mpi', default=False, description='Enable MPI')
    variant('cuda', default=False, description='Enable CUDA')
    variant('papi', default=False, description='Enable papi, a hardware counter software')
    variant('starpu', default=False, description='Enable StarPU')

    depends_on("mpi", when='+mpi')
    depends_on("cuda", when='+cuda')
    depends_on("papi", when='+papi')
    depends_on("starpu", when='+starpu')

    def install(self, spec, prefix):

        # execute bootstrap first (recursive autoreconf)
        subprocess.check_call('./bootstrap')

        config_args = ["--prefix=" + prefix]

        if '+mpi' in spec:
            config_args.append("--with-mpi=%s" % spec['mpi'].prefix)

        if '+cuda' in spec:
            config_args.append("--with-cuda=%s" % spec['cuda'].prefix)

        if '+papi' in spec:
            config_args.append("--with-papi=%s" % spec['papi'].prefix)

        if '+starpu' in spec:
            config_args.append("--with-starpu=%s" % spec['starpu'].prefix)

        configure(*config_args)
        make()
        make("install")

    # to use the existing version available in the environment: EZTRACE_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('EZTRACE_DIR'):
            eztraceroot=os.environ['EZTRACE_DIR']
            if os.path.isdir(eztraceroot):
                os.symlink(eztraceroot+"/bin", prefix.bin)
                os.symlink(eztraceroot+"/include", prefix.include)
                os.symlink(eztraceroot+"/lib", prefix.lib)
            else:
                sys.exit(eztraceroot+' directory does not exist.'+' Do you really have openmpi installed in '+eztraceroot+' ?')
        else:
            sys.exit('EZTRACE_DIR is not set, you must set this environment variable to the installation path of your eztrace')
