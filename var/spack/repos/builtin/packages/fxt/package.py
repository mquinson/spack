from spack import *
import os
from subprocess import call
import spack

class Fxt(Package):
    """This library provides efficient support for recording traces"""
    homepage = "http://savannah.nongnu.org/projects/fkt"

    version('0.3.1' , '85b5829ecfe2754ba7213830c7d8f119',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.3.1.tar.gz")
    version('0.3.0' , '1aeb6807bda817163d432087b27ef855',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.3.0.tar.gz")
    version('0.2.14', '2f6bc2ce77e24be4d16523ccb372990e',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.2.14.tar.gz")
    version('0.2.13', 'c688d01cc50945a0cd6364cc39e33b95',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.2.13.tar.gz")
    version('0.2.12', 'd5d910fd818088f01fcf955eed9bc42a',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.2.12.tar.gz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    def install(self, spec, prefix):

        if spec.satisfies("arch=ppc64"):
            pkg_dir = spack.repo.dirname_for_package_name("fxt")
            call(["cp", pkg_dir+"/config.guess", "."])

        configure("--prefix=%s" % prefix)

        # it seems that this patch is required after configure
        mf = FileFilter('tools/fut.h')
        mf.filter('extern pthread_spinlock_t fut_slot_lock;', '//extern pthread_spinlock_t fut_slot_lock;')

        make(parallel=False)
        # The mkdir commands in fxt's install can fail in parallel
        make("install", parallel=False)

    # to use the existing version available in the environment: FXT_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('FXT_DIR'):
            fxtroot=os.environ['FXT_DIR']
            if os.path.isdir(fxtroot):
                os.symlink(fxtroot+"/bin", prefix.bin)
                os.symlink(fxtroot+"/include", prefix.include)
                os.symlink(fxtroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(fxtroot+' directory does not exist.'+' Do you really have openmpi installed in '+fxtroot+' ?')
        else:
            raise RuntimeError('FXT_DIR is not set, you must set this environment variable to the installation path of your fxt')
