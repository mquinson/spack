from spack import *
import os
import spack
import sys
import platform

class EsslBlas(Package):
    """IBM ESSL Blas and Lapack routines"""
    homepage = "http://www-03.ibm.com/systems/power/software/essl/"

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('ESSLROOT') and os.getenv('XLFROOT'):
        esslroot=os.environ['ESSLROOT']
        xlfroot=os.environ['XLFROOT']
        if os.path.isdir(esslroot) and os.path.isdir(xlfroot):
            provides('blas')

    variant('mt', default=False, description="Use Multithreaded version")

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for essl-blas."""
        essllibdir=self.spec.prefix.lib
        xlfroot=os.environ['XLFROOT']
        if spec.satisfies("+mt"):
            module.blaslibname=[os.path.join(essllibdir, "libesslsmp.so")]
        else:
            module.blaslibname=[os.path.join(essllibdir, "libessl.so -L%s/lib -lxlfmath -lxlf90_r") % xlfroot]
        module.blaslibfortname=module.blaslibname


    def install(self, spec, prefix):
        if os.getenv('ESSLROOT'):
            esslroot=os.environ['ESSLROOT']
            if os.path.isdir(esslroot):
                os.symlink(esslroot+"/include", prefix.include)
                os.symlink(esslroot+"/lib", prefix.lib)
            else:
                sys.exit(esslroot+' directory does not exist.'+' Do you really have ESSL installed in '+esslroot+' ?')
        else:
            sys.exit('ESSLROOT environment variable does not exist. Please set ESSLROOT to use the ESSL Blas')
