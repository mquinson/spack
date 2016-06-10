from spack import *
import spack
import os

class Fake(Package):
    """
    A Fake package to store an empty tarball to avoid downloading tarballs for already downloaded packages.
    Concerns "exists" and "src" versions. (so mainly developers)
    """
    pkg_dir = spack.repo.dirname_for_package_name("fake")
    homepage = pkg_dir
    url      = pkg_dir
    version('src', '7b878b76545ef9ddb6f2b61d4c4be833', url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
    	return 0
