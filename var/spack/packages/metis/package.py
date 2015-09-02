from spack import *
import os

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

    def install(self, spec, prefix):
        if spec.satisfies('@5:'):
            cmake(".",
                  '-DGKLIB_PATH=%s/GKlib' % pwd(),
                  '-DCMAKE_C_COMPILER=mpicc',
                  '-DCMAKE_CXX_COMPILER=mpicxx',
                  '-DSHARED=1',
                  *std_cmake_args)

            make()
            make("install")
        else:
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
            install('libmetis.a', prefix.lib)
