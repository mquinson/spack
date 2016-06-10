from spack import *
import os
import platform
from subprocess import call
import spack

class NetlibBlacs(Package):
    """The BLACS (Basic Linear Algebra Communication Subprograms) project is an ongoing investigation whose purpose is to create a linear algebra oriented message passing interface that may be implemented efficiently and uniformly across a large range of distributed memory platforms."""

    homepage = "http://www.netlib.org/blacs/"

    # tarball has no version, but on the date below, this MD5 was correct.
    version('1997-05-05', '28ae5b91b3193402fe1ae8d06adcf500', url='http://www.netlib.org/blacs/mpiblacs.tgz')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    provides('blacs')

    depends_on('mpi')

    variant('shared', default=True, description='Build BLACS as a shared library')


    def setup(self):
        spec = self.spec
        call(['cp', 'BMAKES/Bmake.MPI-LINUX', 'Bmake.inc'])
        mf = FileFilter('Bmake.inc')

        mf.filter('\$\(HOME\)/BLACS', '%s' % os.getcwd())
        mf.filter('/usr/local/mpich', '%s' % self.spec['mpi'].prefix)
        mf.filter('\$\(MPILIBdir\)/libmpich\.a', '')
        mf.filter('\$\(MPIdir\)/lib/', '')
        mf.filter('INTFACE\s*=.*', 'INTFACE=-DAdd_')
        mf.filter('TRANSCOMM\s*=.*', 'TRANSCOMM=')
        mpi = spec['mpi'].prefix
        try:
            mpicc = spec['mpi'].mpicc
        except NameError:
            mpicc = 'mpicc'
        try:
            mpif77 = spec['mpi'].mpif77
        except NameError:
            mpif77 = 'mpif77'
        mf.filter('F77            = g77', 'F77            = %s' % mpif77)
        mf.filter('CC             = gcc', 'CC             = %s' % mpicc)

        sf=FileFilter('SRC/MPI/Makefile')
        sf.filter('\$\(BLACSLIB\) \$\(Fintobj\)', '$(BLACSLIB) $(Fintobj) $(internal)')
        sf.filter('\$\(ARCH\) \$\(ARCHFLAGS\) \$\(BLACSLIB\) \$\(internal\)', 'mv $(internal) ..')

        if spec.satisfies('+shared'):
            mf.filter('ARCH\s*=.*', 'ARCH=$(CC)')
            if platform.system() == 'Darwin':
                mf.filter('ARCHFLAGS\s*=.*', 'ARCHFLAGS=-shared -undefined dynamic_lookup -o ')
            else:
                mf.filter('ARCHFLAGS\s*=.*', 'ARCHFLAGS=-shared -o ')
            mf.filter('RANLIB\s*=.*', 'RANLIB=echo')
            mf.filter('CCFLAGS\s*=', 'CCFLAGS = -fPIC ')
            mf.filter('F77FLAGS\s*=', 'F77FLAGS = -fPIC ')
            if platform.system() == 'Darwin':
                mf.filter('\.a', '.dylib')
            else:
                mf.filter('\.a', '.so')

        #filter_file('\$\(MAKE\) -f \.\./Makefile I_int \"dlvl=\$\(BTOPdir\)\" \)','echo $(BLACSDEFS) $(MAKE) -f ../Makefile I_int "dlvl=$(BTOPdir)" )', 'SRC/MPI/Makefile')
        call(['cat', 'Bmake.inc'])
        call(['cat', 'SRC/MPI/Makefile'])

    def install(self, spec, prefix):

        self.setup()
        make('mpi')
        mkdirp(prefix.lib)
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
        else:
            libext=".a"

        for l in ["blacsCinit", "blacsF77init", "blacs"]:
            install('LIB/%s_MPI-LINUX-0%s'%(l, libext), '%s/lib%s%s' % (prefix.lib, l, libext))

    # to use the existing version available in the environment: BLACS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BLACS_DIR'):
            netlibblacsroot=os.environ['BLACS_DIR']
            if os.path.isdir(netlibblacsroot):
                os.symlink(netlibblacsroot+"/bin", prefix.bin)
                os.symlink(netlibblacsroot+"/include", prefix.include)
                os.symlink(netlibblacsroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(netlibblacsroot+' directory does not exist.'+' Do you really have openmpi installed in '+netlibblacsroot+' ?')
        else:
            raise RuntimeError('BLACS_DIR is not set, you must set this environment variable to the installation path of your netlib-blacs')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for netlib-blacs."""
        self.spec.cc_link="-L%s -lblacsCinit -lblacsF77init -lblacs" % self.spec.prefix.lib