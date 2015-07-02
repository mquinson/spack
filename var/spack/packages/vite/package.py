from spack import *

class Vite(Package):
    """a tool to visualize execution traces in Paje or OTF format for debugging and profiling parallel or distributed applications."""
    homepage = "http://vite.gforge.inria.fr/"
    url      = "https://gforge.inria.fr/frs/download.php/27457/vite_1157.tar.gz"

    version('trunk', svn='svn://scm.gforge.inria.fr/svnroot/vite/trunk')

    variant('otf', default=False, description='Enable OTF')

    depends_on("otf", when='+otf')
    #depends_on("qt")
    #depends_on("tau")

    def install(self, spec, prefix):

        with working_dir('spack-build', create=True):

            cmake_args = [
                "..",
                "-DBUILD_SHARED_LIBS=ON"]
            cmake_args.extend(["-DUSE_QT5=ON"])

            if '+otf' in spec:
                # Enable OTF here.
                cmake_args.extend(["-DVITE_ENABLE_OTF=ON"])

            cmake_args.extend(std_cmake_args)
            cmake(*cmake_args)
            make()
            make("install")
