from spack import *
import os
from subprocess import call

class Blacs(Package):
    """The BLACS (Basic Linear Algebra Communication Subprograms) project is an ongoing investigation whose purpose is to create a linear algebra oriented message passing interface that may be implemented efficiently and uniformly across a large range of distributed memory platforms."""

    homepage = "http://www.netlib.org/blacs/"

    # tarball has no version, but on the date below, this MD5 was correct.
    # version('1997-05-05', '28ae5b91b3193402fe1ae8d06adcf500', url='http://www.netlib.org/blacs/mpiblacs.tgz')
    version('lib','82687f1e07fd98e0b9f78b71911459fe', url='http://www.netlib.org/blacs/archives/blacs_MPI-LINUX-0.tgz')
    depends_on('mpich')

    # def patch(self):
    	# os.symlink('BMAKES/Bmake.PVM-LINUX', 'Bmake.inc')
        # mf = FileFilter('Bmake.inc')

        # mf.filter('MPIdir = /usr/local/mpich', 'MPIdir = %s' % self.spec['mpich'].prefix)
        # mf.filter('/bin/sh', '/bin/bash')

    def install(self, spec, prefix):
        # make('all')
        mkdirp(prefix.lib)
        mkdirp(prefix.include)
        call(['ls'])
        install('./blacsCinit_MPI-LINUX-0.a', '%s/libblacsCinit-openmpi.a' % prefix.lib)
        install('./blacsF77init_MPI-LINUX-0.a', '%s/libblacsF77init-openmpi.a' % prefix.lib)
        install('./blacs_MPI-LINUX-0.a', '%s/libblacs-openmpi.a' % prefix.lib)

        	    



