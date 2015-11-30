from spack import *

class Simgrid(Package):
    """To study the behavior of large-scale distributed systems such as Grids, Clouds, HPC or P2P systems."""
    homepage = "http://simgrid.gforge.inria.fr/index.html"
    url      = "http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz"


    version('3.12', 'd73faaf81d7a9eb0d309cfd72532c5f1',
            url='http://gforge.inria.fr/frs/download.php/file/35215/SimGrid-3.12.tar.gz')
    version('3.11', '358ed81042bd283348604eb1beb80224',
            url='http://gforge.inria.fr/frs/download.php/file/33683/SimGrid-3.11.tar.gz')
    version('3.10', 'a345ad07e37539d54390f817b7271de7',
            url='http://gforge.inria.fr/frs/download.php/file/33124/SimGrid-3.10.tar.gz')

    def install(self, spec, prefix):
        cmake('.', *std_cmake_args)
        make()
        make("install")
