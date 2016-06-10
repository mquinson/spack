from spack import *
import os
import spack
import sys
import platform

class Essl(Package):
    """IBM ESSL Blas and Lapack routines"""
    homepage = "http://www-03.ibm.com/systems/power/software/essl/"

    version('with-netlib', 'f2f6c67134e851fe189bb3ca1fbb5101',
            url="http://www.netlib.org/lapack/lapack-3.6.0.tgz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")

    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    # virtual dependency
    provides('blas')
    provides('lapack')

    variant('mt', default=False, description="Use Multithreaded version")
    # used for netlib-lapack
    variant('shared', default=True, description="Build netlib-lapack shared library version")

    # used to build netlib-lapack release which is needed because essl does not
    # provide a complete blas/lapack interface
    depends_on('cmake')


    # Null literal string is not permitted with xlf
    def patch_xlf(self):

        mf = FileFilter('SRC/xerbla_array.f')
        mf.filter('SRNAME = \'\'', 'SRNAME = \' \'')

    def install(self, spec, prefix):

        if spec.satisfies('%xl'):
            self.patch_xlf()

        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        cmake_args.extend([
            "-Wno-dev",
            "-DBUILD_TESTING:BOOL=ON",
            "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
            "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

        if spec.satisfies('+shared'):
            cmake_args.append('-DBUILD_SHARED_LIBS=ON')
            cmake_args.append('-DBUILD_STATIC_LIBS=OFF')
            if platform.system() == 'Darwin':
                cmake_args.append('-DCMAKE_SHARED_LINKER_FLAGS=-undefined dynamic_lookup')
        cmake_args.append('-DCMAKE_INSTALL_LIBDIR=lib')
        if spec.satisfies("%xl"):
            cmake_args.extend(["-DCMAKE_Fortran_FLAGS=-O3 -qpic -qhot -qtune=auto -qarch=auto"])

        cmake(*cmake_args)
        make()
        make("install")

    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('ESSLROOT') and os.getenv('XLFROOT') and os.getenv('XLSMPROOT'):
            esslroot=os.environ['ESSLROOT']
            xlfroot=os.environ['XLFROOT']
            xlsmproot=os.environ['XLSMPROOT']
            if os.path.isdir(esslroot) and os.path.isdir(xlfroot) and os.path.isdir(xlsmproot):
                os.symlink(esslroot+"/include", prefix.include)
                os.symlink(esslroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(esslroot+' directory does not exist.'+' Do you really have ESSL installed in '+esslroot+' ?')
        else:
            raise RuntimeError('ESSLROOT or XLFROOT or XLSMPROOT environment variable does not exist. Please set ESSLROOT and XLFROOT and XLSMPROOT, where lies libessl and libxlf90 and xlsmp, to use the ESSL')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for essl."""

        if spec.satisfies('@exist'):
            netlib_lapack_libs = ""
        else:
            # set netlib-lapack lib
            if os.path.isdir(spec.prefix.lib64):
                libdir = self.spec.prefix+"/lib64"
            else:
                libdir = self.spec.prefix+"/lib"
            netlib_lapack_libs = "-L%s -llapack -lblas" % libdir

        # set essl lib
        esslroot=os.environ['ESSLROOT']
        xlfroot=os.environ['XLFROOT']
        xlsmproot=os.environ['XLSMPROOT']
        if os.path.isdir(esslroot) and os.path.isdir(xlfroot) and os.path.isdir(xlsmproot):
            self.spec.cc_link_mt = "-L%s -R%s -lesslsmp -L%s -lxlsmp -L%s -lxlfmath -lxlf90 -lxlf90_r %s -lesslsmp -lxlsmp -lxlfmath -lxlf90 -lxlf90_r" %(esslroot,esslroot,xlsmproot,xlfroot,netlib_lapack_libs)
            self.spec.cc_link    = "-L%s -R%s -lessl -L%s -lxlsmp -L%s -lxlfmath -lxlf90 -lxlf90_r %s -lxlfmath -lxlf90 -lxlf90_r" % (esslroot,esslroot,xlsmproot,xlfroot,netlib_lapack_libs)
            self.spec.fc_link_mt = self.spec.cc_link_mt
            self.spec.fc_link    = self.spec.cc_link
        else:
            raise RuntimeError('ESSLROOT or XLFROOT or XLSMPROOT environment variable does not exist. Please set ESSLROOT and XLFROOT and XLSMPROOT, where lies libessl and libxlf90 and xlsmp, to use the ESSL')