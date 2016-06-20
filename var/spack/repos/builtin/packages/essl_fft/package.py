from spack import *
import os
import spack
import sys
import platform

class Essl_fftw(Package):
    """IBM ESSL FFTW3 routines"""
    homepage = "http://www-03.ibm.com/systems/power/software/essl/"

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    provides('fft')

    depends_on('essl')

    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('ESSLFFTROOT'):
            esslroot=os.environ['ESSLFFTROOT']
            if os.path.isdir(esslroot):
                os.symlink(esslroot+"/include", prefix.include)
                os.symlink(esslroot+"/lib", prefix.lib)
                os.symlink(esslroot+"/lib64", prefix.lib64)
            else:
                raise RuntimeError(esslroot+' directory does not exist.'+' Do you really have ESSL FFTW installed in '+esslroot+' ?')
        else:
            raise RuntimeError('ESSLFFTROOT environment variable does not exist. Please set ESSLFFTROOT, where lies include/fftw3_essl.h and lib64/libfftw3_essl.a (or .so)')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for fftw_essl."""
        spec = self.spec
        esslroot=os.environ['ESSLFFTROOT']
        if os.path.isdir(esslroot):
            spec.cc_link_mt = "-L%s -lfftw3_essl %s" % (esslroot,spec['essl'].cc_link_mt)
            spec.cc_link    = "-L%s -lfftw3_essl %s" % (esslroot,spec['essl'].cc_link)
            spec.fc_link_mt = "-L%s -lfftw3_essl %s" % (esslroot,spec['essl'].fc_link_mt)
            spec.fc_link    = "-L%s -lfftw3_essl %s" % (esslroot,spec['essl'].fc_link)
        else:
            raise RuntimeError('ESSLFFTROOT environment variable does not exist. Please set ESSLFFTROOT, where lies include/fftw3_essl.h and lib64/libfftw3_essl.a (or .so)')