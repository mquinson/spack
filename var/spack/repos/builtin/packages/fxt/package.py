from spack import *
import os
from subprocess import call
import spack

class Fxt(Package):
    """This library provides efficient support for recording traces"""
    homepage = "http://savannah.nongnu.org/projects/fkt"

    version('0.3.3' , '52055550a21655a30f0381e618081776',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.3.3.tar.gz")

    variant('moreparams', default=False, description='Increase the value of FXT_MAX_PARAMS (to allow longer task names).')

    def install(self, spec, prefix):

        if spec.satisfies("arch=linux-ppc64le"):
            pkg_dir = spack.repo.dirname_for_package_name("fxt")
            call(["cp", pkg_dir+"/config.guess", "."])

        os.environ["CFLAGS"] = "-fPIC"
        configure("--prefix=%s" % prefix)

        # Increase the value of FXT_MAX_PARAMS (to allow longer task names)
        if '+moreparams' in spec:
            mf = FileFilter('tools/fxt.h')
            mf.filter('#define FXT_MAX_PARAMS.*', '#define FXT_MAX_PARAMS 16')

        make(parallel=False)
        # The mkdir commands in fxt's install can fail in parallel
        make("install", parallel=False)
