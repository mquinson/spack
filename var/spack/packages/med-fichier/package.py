from spack import *
import os
import platform
from subprocess import call

class MedFichier(Package):
    """A libray for scientific data exchange."""
    homepage = "http://www.code-aster.org/outils/med/html/index.html"
    url      = "ftp://ftp.gnome.org/mirror/debian-archive/pool/main/m/med-fichier/med-fichier_2.3.1.orig.tar.gz"

    version('2.3.1', 'caa877fe7c1b3450edaccd729c52844b')

    depends_on("hdf5@1.6.7~mpi")

    variant('shared', default=True, description="Build shared library version")

    def install(self, spec, prefix):
        os.environ['LIBS']="-lm"

        if platform.system() == "Darwin":
            call ("chmod 644 include/med_outils.h src/ci/MEDunvCr.c".split(' '))
            filter_file("#include <malloc.h>", "", "include/med_outils.h")
            filter_file("cuserid", "getpwuid", "src/ci/MEDunvCr.c")

        config_args = ["--prefix=" + prefix]

        if spec.satisfies('+shared'):
            config_args.append("--enable-shared")
        else:
            config_args.append("--disable-shared")
        
        config_args.append("--with-hdf5=%s" % spec['hdf5'].prefix )

        configure(*config_args)
        make()
        make("install")
