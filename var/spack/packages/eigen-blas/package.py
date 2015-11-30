from spack import *
import os
import platform

class EigenBlas(Package):
    """Eigen BLAS"""
    homepage = "http://eigen.tuxfamily.org/index.php?title=Main_Page"
    url      = "http://bitbucket.org/eigen/eigen/get/3.2.7.tar.bz2"

    version('3.3-alpha1', 'b49260a4cac64f829bf5396c2150360e')
    version('3.2.7', 'cc1bacbad97558b97da6b77c9644f184')
    version('hg-default', hg='https://bitbucket.org/eigen/eigen/')

    # virtual dependency
    provides('blas')

    variant('shared', default=True, description='Build Eigen BLAS as a shared library')

    depends_on('cmake')

    def setup_dependent_environment(self, module, spec, dep_spec):
        """Dependencies of this package will get the library name for eigen-blas."""
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
        else:
            libext=".a"
        module.blaslibname=[os.path.join(self.spec.prefix.lib, "libeigen_blas%s" % libext)]
        module.blaslibfortname = module.blaslibname

    def install(self, spec, prefix):

        # configure and build process
        with working_dir('spack-build', create=True):
            cmake_args = [
                "..",
                "-DEIGEN_TEST_NOQT=ON",
                "-DEIGEN_TEST_NO_OPENGL=ON"]

            if spec.satisfies('@3.3:') or spec.satisfies('@hg-default'):
                cmake_args.extend(["-DCMAKE_CXX_FLAGS=-march=native -mtune=native"])

            cmake_args += std_cmake_args
            cmake(*cmake_args)
            make('blas')

        # installation process
        # we copy the library: blas is a subproject of eigen, there is no specific rule to install blas solely
        if spec.satisfies('+shared'):
            libext=".dylib" if platform.system() == 'Darwin' else ".so"
            eigenblaslibname="libeigen_blas%s" % libext
        else:
            libext=".a"
            eigenblaslibname="libeigen_blas_static.a"
        blaslibname="libeigen_blas%s" % libext
        mkdirp('%s/lib'%prefix)
        install('spack-build/blas/%s'%eigenblaslibname, '%s/lib/%s'%(prefix, blaslibname))
