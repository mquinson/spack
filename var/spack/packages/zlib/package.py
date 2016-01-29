from spack import *
import spack
import os, platform

class Zlib(Package):
    """zlib is designed to be a free, general-purpose, legally unencumbered --
       that is, not covered by any patents -- lossless data-compression library for
       use on virtually any computer hardware and operating system.
    """

    homepage = "http://zlib.net"
    url      = "http://zlib.net/zlib-1.2.8.tar.gz"

    version('1.2.8', '44d667c142d7cda120332623eab69f40')

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

    # to use the existing version available in the environment: MUMPS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        os.chdir(self.get_env_dir(self.name.upper()+'_DIR'))
        os.symlink("bin", prefix.bin)
        os.symlink("lib", prefix.lib)

    # to use the existing version available in the system
    @when('@system')
    def install(self, spec, prefix):
        os.symlink("/usr/bin", prefix.bin)
        os.symlink("/usr/lib", prefix.lib)
