from spack import *
import os
import spack
import sys
import platform

class EsslLapack(Package):
    """IBM ESSL Blas and Lapack routines"""
    homepage = "http://www-03.ibm.com/systems/power/software/essl/"

    version('with-netlib', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")

    pkg_dir = spack.db.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    if os.getenv('ESSLROOT') and os.getenv('XLFROOT') and os.getenv('XLSMPROOT'):
        esslroot=os.environ['ESSLROOT']
        xlfroot=os.environ['XLFROOT']
        xlsmproot=os.environ['XLSMPROOT']
        if os.path.isdir(esslroot) and os.path.isdir(xlfroot) and os.path.isdir(xlsmproot):
            provides('lapack')

    variant('mt', default=False, description="Use Multithreaded version")

    # blas is a virtual dependency.
    depends_on('blas')

    depends_on('cmake')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the libraries names for essl-lapack."""

        if spec.satisfies('@exist'):
            netlib_lapack_libs = ""
        else:
            # set netlib-lapack lib
            if os.path.isdir(spec.prefix.lib64):
                libdir = self.spec.prefix+"/lib64"
            if os.path.isdir(spec.prefix.lib):
                libdir = self.spec.prefix+"/lib"
            netlib_lapack_libs = "-L%s -llapack" % libdir

        # set essl lib
        esslroot=os.environ['ESSLROOT']
        xlfroot=os.environ['XLFROOT']
        if os.path.isdir(esslroot) and os.path.isdir(xlfroot):
            if spec.satisfies("+mt"):
                xlsmproot=os.environ['XLSMPROOT']
                if os.path.isdir(xlfroot):
                    module.lapacklibname=["-L%s -R%s -lesslsmp -L%s -lxlsmp -L%s -lxlfmath -lxlf90 -lxlf90_r %s -lesslsmp -lxlsmp -lxlfmath -lxlf90 -lxlf90_r" %(esslroot,esslroot,xlsmproot,xlfroot,netlib_lapack_libs)]
                else:
                    sys.exit('XLSMPROOT environment variable does not exist. Please set XLSMPROOT, where lies libxlsmp, to use the ESSL LAPACK')
            else:
                module.lapacklibname=["-L%s -R%s -lessl -L%s -lxlfmath -lxlf90 -lxlf90_r %s -lxlfmath -lxlf90 -lxlf90_r" % (esslroot,esslroot,xlfroot,netlib_lapack_libs)]
            module.lapacklibfortname=module.lapacklibname
        else:
            sys.exit('ESSLROOT or XLFROOT environment variable does not exist. Please set ESSLROOT and XLFROOT, where lies libessl and libxlf90, to use the ESSL Blas')

    # Null literal string is not permitted with xlf
    def patch_xlf(self):

        mf = FileFilter('SRC/xerbla_array.f')
        mf.filter('SRNAME = \'\'', 'SRNAME = \' \'')

    def install(self, spec, prefix):

        if spec.satisfies('%xl'):
            self.patch_xlf()

        cmake_args = ["."]
        cmake_args += std_cmake_args
        cmake_args += ["-Wno-dev", "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]

        blas_libs = " ".join(blaslibfortname)
        blas_libs = blas_libs.replace(' ', ';')
        cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])
        cmake_args.append('-DBUILD_SHARED_LIBS=ON')
        cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
        cmake_args.append('-DCMAKE_INSTALL_LIBDIR=lib')
        if platform.system() == 'Darwin':
            cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')

        cmake(*cmake_args)
        make()
        make("install")

    @when('@exist')
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
