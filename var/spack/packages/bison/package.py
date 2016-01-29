from spack import *
import spack
import os, platform

class Bison(Package):
    """Bison is a general-purpose parser generator that converts
    an annotated context-free grammar into a deterministic LR or
    generalized LR (GLR) parser employing LALR(1) parser tables."""

    homepage = "http://www.gnu.org/software/bison/"
    url      = "http://ftp.gnu.org/gnu/bison/bison-3.0.tar.gz"

    version('3.0.4', 'a586e11cd4aff49c3ff6d3b6a4c9ccf8')

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('system', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        configure("--prefix=%s" % prefix)

        make()
        make("install")

    # to use the existing version available in the environment: BISON_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        os.symlink("bin", prefix.bin)

    # to use the existing version available in the system
    @when('@system')
    def install(self, spec, prefix):
        os.symlink("/usr/bin", prefix.bin)
