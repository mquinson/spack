from spack import *
import os
import spack
import sys
import platform

class EsslLapack(Package):
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
            provides('lapack')

    variant('mt', default=False, description="Use Multithreaded version")

    # blas is a virtual dependency.
    depends_on('blas')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for essl-lapack."""
        esslroot=os.environ['ESSLROOT']
        xlfroot=os.environ['XLFROOT']
        if os.path.isdir(esslroot):
            if spec.satisfies("+mt"):
                xlsmproot=os.environ['XLSMPROOT']
                if os.path.isdir(xlfroot):
                    module.lapacklibname=["-L%s/lib -R%s/lib -lesslsmp -L%s/lib -lxlsmp" %(esslroot,esslroot,xlsmproot)]
                else:
                    sys.exit('XLSMPROOT environment variable does not exist. Please set XLSMPROOT, where lies libxlsmp, to use the ESSL LAPACK')
            else:
                module.lapacklibname=["-L%s/lib -R%s/lib -lessl" % (esslroot,esslroot)]
            module.lapacklibfortname=module.lapacklibname
        else:
            sys.exit('ESSLROOT environment variable does not exist. Please set ESSLROOT, where lies libessl, to use the ESSL LAPACK')

    def install(self, spec, prefix):
        if os.getenv('ESSLROOT'):
            esslroot=os.environ['ESSLROOT']
            if os.path.isdir(esslroot):
                os.symlink(esslroot+"/include", prefix.include)
                os.symlink(esslroot+"/lib", prefix.lib)
            else:
                sys.exit(esslroot+' directory does not exist.'+' Do you really have ESSL installed in '+esslroot+' ?')
        else:
            sys.exit('ESSLROOT environment variable does not exist. Please set ESSLROOT, where lies libessl, to use the ESSL LAPACK')
