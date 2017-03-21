from spack import *
import spack

class IbBgmresDr(Package):
    """Library implementing Block-GMres with Inexact Breakdown and Deflated Restarting"""

    homepage = "https://gforge.inria.fr/projects/ib-bgmres-dr/"
    
    version('develop', git='https://scm.gforge.inria.fr/anonscm/git/ib-bgmres-dr/ib-bgmres-dr.git', branch='ib', preferred=True)

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('debug', default=False, description='Enable debug symbols')
    variant('shared', default=True, description='Build as shared library')
    
    depends_on("cmake")
    depends_on("blas")
    depends_on("lapack")
    
    def install(self, spec, prefix):
        
        with working_dir('spack-build', create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON",
                "-DIBBGMRESDR_BUILD_WARNINGS=OFF"])

            cmake_args.extend(["-DCMAKE_EXE_LINKER_FLAGS=-lstdc++"])

            if spec.satisfies('+shared'):
                # Enable build shared libs
                cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])

            if spec.satisfies('+debug'):                
                cmake_args.extend(["-DIBBGMRESDR_DEBUG_MODE=ON"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])

            # Blas
            blas_libs = spec['blas'].cc_link
            cmake_args.extend(["-DBLAS_LIBRARIES=" + str(blas_libs).replace("-Wl,--no-as-needed ", "")])

            # Lapack
            lapack_libs = spec['lapack'].cc_link
            cmake_args.extend(["-DLAPACK_LIBRARIES=" + str(lapack_libs).replace("-Wl,--no-as-needed ", "")])

            cmake(*cmake_args)
            make()
            make("install")

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for ib-bgmres-dr."""        
        self.spec.cc_link="-L%s -libgmresdr" % self.spec.prefix.lib
        self.spec.fc_link=self.spec.cc_link
