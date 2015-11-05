from spack import *
import os
import platform
from subprocess import call

class NetlibBlacs(Package):
    """The BLACS (Basic Linear Algebra Communication Subprograms) project is an ongoing investigation whose purpose is to create a linear algebra oriented message passing interface that may be implemented efficiently and uniformly across a large range of distributed memory platforms."""

    homepage = "http://www.netlib.org/blacs/"

    # tarball has no version, but on the date below, this MD5 was correct.
    version('1997-05-05', '28ae5b91b3193402fe1ae8d06adcf500', url='http://www.netlib.org/blacs/mpiblacs.tgz')
    version('lib','82687f1e07fd98e0b9f78b71911459fe', url='http://www.netlib.org/blacs/archives/blacs_MPI-LINUX-0.tgz')

    provides('blacs')

    depends_on('mpi')

    variant('shared', default=True, description='Build BLACS as a shared library')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for netlib-blacs."""
        lib_dir = self.spec.prefix.lib
        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                module.blacslibname=[os.path.join(lib_dir, "libblacsCinit.dylib"), os.path.join(lib_dir, "libblacsF77init.dylib"), os.path.join(lib_dir, "libblacs.dylib")]
            else:
                module.blacslibname=[os.path.join(lib_dir, "libblacsCinit.so"), os.path.join(lib_dir, "libblacsF77init.so"), os.path.join(lib_dir, "libblacs.so") ]
        else:
            module.blacslibname=[os.path.join(lib_dir, "libblacsCinit.a"), os.path.join(lib_dir, "libblacsF77init.a"), os.path.join(lib_dir, "libblacs.a") ]

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
        mf.filter('F77            = g77', 'F77            = mpif77')
        mf.filter('CC             = gcc', 'CC             = mpicc')

        sf=FileFilter('SRC/MPI/Makefile')
        sf.filter('\$\(BLACSLIB\) \$\(Fintobj\)', '$(BLACSLIB) $(Fintobj) $(internal)')
        sf.filter('\$\(ARCH\) \$\(ARCHFLAGS\) \$\(BLACSLIB\) \$\(internal\)', 'mv $(internal) ..')

        if spec.satisfies('+shared'):
            mf.filter('ARCH\s*=.*', 'ARCH=$(CC)')
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
            if platform.system() == 'Darwin':
                install('LIB/blacsCinit_MPI-LINUX-0.so', '%s/libblacsCinit.dylib' % prefix.lib)
                install('LIB/blacsF77init_MPI-LINUX-0.so', '%s/libblacsF77init.dylib' % prefix.lib)
                install('LIB/blacs_MPI-LINUX-0.so', '%s/libblacs.dylib' % prefix.lib)
            else:
                install('LIB/blacsCinit_MPI-LINUX-0.so', '%s/libblacsCinit.so' % prefix.lib)
                install('LIB/blacsF77init_MPI-LINUX-0.so', '%s/libblacsF77init.so' % prefix.lib)
                install('LIB/blacs_MPI-LINUX-0.so', '%s/libblacs.so' % prefix.lib)
        else:
            install('LIB/blacsCinit_MPI-LINUX-0.a', '%s/libblacsCinit.a' % prefix.lib)
            install('LIB/blacsF77init_MPI-LINUX-0.a', '%s/libblacsF77init.a' % prefix.lib)
            install('LIB/blacs_MPI-LINUX-0.a', '%s/libblacs.a' % prefix.lib)
        	    



