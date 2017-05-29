from spack import *
import spack

def get_submodules():
    git = which('git')
    git('submodule', 'update', '--init', '--recursive')

class Fabulous(Package):
    """FABuLOuS (Fast Accurate Block Linear krylOv Solver)
    Library implementing Block-GMres with Inexact Breakdown and Deflated Restarting"""

    homepage = "https://gforge.inria.fr/projects/ib-bgmres-dr/"
    gitroot= "https://scm.gforge.inria.fr/anonscm/git/ib-bgmres-dr/ib-bgmres-dr.git"
    version("develop", git=gitroot,  branch="develop", preferred=True)
    version("ib", git=gitroot, branch="ib")
    version("0.3", git=gitroot, branch="release_v0.3")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    version("exist", "7b878b76545ef9ddb6f2b61d4c4be833",
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version("src")
    variant("shared", default=True, description="Build as shared library")
    variant("debug", default=False, description="Enable debug symbols")
    variant("chameleon", default=False, description="build extra chameleon backend")
    variant("examples", default=False, description="build examples and tests")
    variant("blasmt", default=False, description="use multi-threaded blas and lapack kernels")

    depends_on("cmake")
    depends_on("cblas")
    depends_on("lapacke")
    depends_on("chameleon@master", when="+chameleon")

    def install(self, spec, prefix):

        if spec.satisfies("@develop"):
            get_submodules()

        with working_dir("spack-build", create=True):
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend([
                "-Wno-dev",
                "-DCMAKE_COLOR_MAKEFILE:BOOL=ON",
                "-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"])

            # old versions of cmake use gcc instead of g++
            # to link a C application with a C++ library:
            cmake_args.extend(["-DCMAKE_EXE_LINKER_FLAGS=-lstdc++"])

            if spec.satisfies('+blasmt~chameleon'):
                blas_libs = self.spec['blas'].cc_link_mt
            else:
                if spec.satisfies('+blasmt'):
                    print("Warning: +blasmt variant is ignored when +chameleon is given")
                blas_libs = self.spec['blas'].cc_link

            blas_libs = blas_libs.replace(' ', ';');
            cmake_args.extend(['-DBLAS_LIBRARIES=%s' % blas_libs])

            if spec.satisfies("+shared"):
                # Enable build shared libs
                cmake_args.extend(["-DBUILD_SHARED_LIBS=ON"])
            else:
                cmake_args.extend(["-DBUILD_SHARED_LIBS=OFF"])

            if spec.satisfies("+debug"):
                cmake_args.extend(["-DFABULOUS_DEBUG_MODE=ON"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])
            else:
                cmake_args.extend(["-DFABULOUS_DEBUG_MODE=OFF"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=RelWithDebInfo"])

            if spec.satisfies("+chameleon"):
                cham_prefix = spec["chameleon"].prefix
                cmake_args.extend(["-DCHAMELEON_DIR="+cham_prefix])
                cmake_args.extend(["-DFABULOUS_USE_CHAMELEON=ON"])
            else:
                cmake_args.extend(["-DFABULOUS_USE_CHAMELEON=OFF"])

            if spec.satisfies("+examples"):
                cmake_args.extend(["-DFABULOUS_BUILD_EXAMPLES=ON"])
                cmake_args.extend(["-DFABULOUS_BUILD_TESTS=ON"])
            else:
                cmake_args.extend(["-DFABULOUS_BUILD_EXAMPLES=OFF"])
                cmake_args.extend(["-DFABULOUS_BUILD_TESTS=OFF"])

            cmake(*cmake_args)
            make()
            make("install")

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for fabulous."""
        self.spec.cc_link="-L%s -lfabulous" % self.spec.prefix.lib
        self.spec.fc_link=self.spec.cc_link
