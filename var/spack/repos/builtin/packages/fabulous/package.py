from spack import *
import spack

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
    variant("chameleon", default=True, description="Add extra chameleon backend")

    depends_on("cmake")
    depends_on("cblas")
    depends_on("lapacke")
    depends_on("chameleon", when="@develop+chameleon")

    def install(self, spec, prefix):

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

            if spec.satisfies("+shared"):
                # Enable build shared libs
                cmake_args.extend(["-DFABULOUS_BUILD_SHARED_LIBS=ON"])

            if spec.satisfies("+debug"):
                cmake_args.extend(["-DFABULOUS_DEBUG_MODE=ON"])
                cmake_args.extend(["-DCMAKE_BUILD_TYPE=Debug"])

            if spec.satisfies("@develop+chameleon"):
                cham_prefix = spec["chameleon"].prefix
                print(cham_prefix)
                cmake_args.extend(["-DCHAMELEON_DIR="+cham_prefix])

            cmake(*cmake_args)
            make()
            make("install")

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for fabulous."""
        self.spec.cc_link="-L%s -lfabulous" % self.spec.prefix.lib
        self.spec.fc_link=self.spec.cc_link
