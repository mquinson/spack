from spack import *
import os
import platform
from subprocess import call

class Metis(Package):
    """METIS is a set of serial programs for partitioning graphs,
       partitioning finite element meshes, and producing fill reducing
       orderings for sparse matrices. The algorithms implemented in
       METIS are based on the multilevel recursive-bisection,
       multilevel k-way, and multi-constraint partitioning schemes."""

    homepage = "http://glaros.dtc.umn.edu/gkhome/metis/metis/overview"
    url      = "http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz"

    version('5.1.0', '5465e67079419a69e0116de24fce58fe',
            url='http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz')
    version('4.0.3', 'd3848b454532ef18dc83e4fb160d1e10',
            url='http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/OLD/metis-4.0.3.tar.gz')

    depends_on('mpi', when='@5:')

    variant('shared', default=True, description='Build METIS as a shared library')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for Metis."""
        module.metislibname=[os.path.join(self.spec.prefix.lib, "libmetis.a")]
        if spec.satisfies('+shared'):
            if platform.system() == 'Darwin':
                module.metislibname=[os.path.join(self.spec.prefix.lib, "libmetis.dylib")]
            else:
                module.metislibname=[os.path.join(self.spec.prefix.lib, "libmetis.so")]


    def install(self, spec, prefix):
        if spec.satisfies('@5:'):
            if spec.satisfies('+shared'):
                cmake(".",
                      '-DGKLIB_PATH=%s/GKlib' % pwd(),
                      '-DSHARED=1',
                      *std_cmake_args)
            else:
                cmake(".",
                      '-DGKLIB_PATH=%s/GKlib' % pwd(),
                      '-DSHARED=0',
                      *std_cmake_args)
            make()
            make("install")
        else:
            if spec.satisfies('+shared'):
                mf = FileFilter('Makefile.in')
                mf.filter('COPTIONS\s*=', 'COPTIONS = -fPIC ')

            make()

            # No install provided
            mkdirp('%s/Lib' % prefix)
            mkdirp(prefix.include)
            with working_dir('Lib'):
                for file in os.listdir("%s" % self.stage.path + "/metis-%s/Lib" % spec.version):
                    if file.endswith(".h"):
                        install(file, '%s/Lib' % prefix)
                        install(file, prefix.include)

            mkdirp(prefix.lib)
            if spec.satisfies('+shared'):
                if platform.system() == 'Darwin':
                    call(['cc', '-shared', '-undefined dynamic_lookup', '-o', 'libmetis.dylib', '-Wl,--whole-archive', 'libmetis.a', '-Wl,--no-whole-archive'])
                    install('libmetis.dylib', prefix.lib)
                else:
                    call(['cc', '-shared', '-o', 'libmetis.so', '-Wl,--whole-archive', 'libmetis.a', '-Wl,--no-whole-archive'])
                    install('libmetis.so', prefix.lib)
            else:
                install('libmetis.a', prefix.lib)
