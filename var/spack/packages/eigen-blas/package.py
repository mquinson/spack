from spack import *
import os
import platform
import spack

class EigenBlas(Package):
    """Eigen BLAS"""
    homepage = "http://eigen.tuxfamily.org/index.php?title=Main_Page"

    version('3.3-beta1', '9c31064e1cd7ac3a32771c9116549259',
            url = "http://bitbucket.org/eigen/eigen/get/3.3-beta1.tar.bz2")
    version('3.3-alpha1', 'b49260a4cac64f829bf5396c2150360e',
            url = "http://bitbucket.org/eigen/eigen/get/3.3-alpha1.tar.bz2")
    version('3.2.7', 'cc1bacbad97558b97da6b77c9644f184',
            url = "http://bitbucket.org/eigen/eigen/get/3.2.7.tar.bz2")
    version('hg-default', hg='https://bitbucket.org/eigen/eigen/')

    pkg_dir = spack.db.dirname_for_package_name("eigen-blas")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

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
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DEIGEN_TEST_NOQT=ON"])
            cmake_args.extend(["-DEIGEN_TEST_NO_OPENGL=ON"])

            if spec.satisfies('@3.3:') or spec.satisfies('@hg-default'):
                cmake_args.extend(["-DCMAKE_CXX_FLAGS=-march=native"])

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

    # to use the existing version available in the environment: BLAS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('BLAS_DIR'):
            eigenblasroot=os.environ['BLAS_DIR']
            if os.path.isdir(eigenblasroot):
                os.symlink(eigenblasroot+"/bin", prefix.bin)
                os.symlink(eigenblasroot+"/include", prefix.include)
                os.symlink(eigenblasroot+"/lib", prefix.lib)
            else:
                sys.exit(eigenblasroot+' directory does not exist.'+' Do you really have openmpi installed in '+eigenblasroot+' ?')
        else:
            sys.exit('BLAS_DIR is not set, you must set this environment variable to the installation path of your eigenblas')
