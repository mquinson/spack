from spack import *
import os
import spack

class Papi(Package):
    """PAPI provides the tool designer and application engineer with a
       consistent interface and methodology for use of the performance
       counter hardware found in most major microprocessors. PAPI
       enables software engineers to see, in near real time, the
       relation between software performance and processor events.  In
       addition Component PAPI provides access to a collection of
       components that expose performance measurement opportunites
       across the hardware and software stack."""
    homepage = "http://icl.cs.utk.edu/papi/index.html"

    version('5.4.1', '9134a99219c79767a11463a76b0b01a2',
            url="http://icl.cs.utk.edu/projects/papi/downloads/papi-5.4.1.tar.gz")
    version('5.3.0', '367961dd0ab426e5ae367c2713924ffb',
            url="http://icl.cs.utk.edu/projects/papi/downloads/papi-5.3.0.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("papi")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))

    def install(self, spec, prefix):
        os.chdir("src/")

        configure_args=["--prefix=%s" % prefix]

        # PAPI uses MPI if MPI is present; since we don't require an
        # MPI package, we ensure that all attempts to use MPI fail, so
        # that PAPI does not get confused
        configure_args.append('MPICC=:')

        configure(*configure_args)

        make()
        make("install")

    # to use the existing version available in the environment: PAPI_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('PAPI_DIR'):
            papiroot=os.environ['PAPI_DIR']
            if os.path.isdir(papiroot):
                os.symlink(papiroot+"/bin", prefix.bin)
                os.symlink(papiroot+"/include", prefix.include)
                os.symlink(papiroot+"/lib", prefix.lib)
            else:
                sys.exit(papiroot+' directory does not exist.'+' Do you really have openmpi installed in '+papiroot+' ?')
        else:
            sys.exit('PAPI_DIR is not set, you must set this environment variable to the installation path of your papi')
