from spack import *
import spack
import os, platform

class Flex(Package):
    """Flex is a tool for generating scanners."""

    homepage = "http://flex.sourceforge.net/"
    url      = "http://download.sourceforge.net/flex/flex-2.5.39.tar.gz"

    # For a reason I dont want to investigate, flex doesnt compile on OSX with macports
    if not platform.system() == 'Darwin':
        version('2.5.39', 'e133e9ead8ec0a58d81166b461244fde', url = "http://download.sourceforge.net/flex/flex-2.5.39.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        configure("--prefix=%s" % prefix)

        make()
        make("install")

    # to use the existing version available in the environment
    @when('@exist')
    def install(self, spec, prefix):
        os.symlink("/usr/bin", prefix.bin)
