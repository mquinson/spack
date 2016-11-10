from spack import *
import os
import getpass
import spack

class Aerosol(Package):
    """Aerosol is a high order Finite Element C++ library. It requires an MPI
       implementation, Pampa (therefore also Scotch), BLAS or Eigen3/IMKL,
       libXML2 and can also utilize HDF5 and PAPI.

       As there is no publically released version of aerosol yet, this package
       requires the user has access to Aerosol's repository on gforge.
          PLEASE MAKE SURE YOUR USERNAME MATCHES YOUR GFORGE ACCOUNT NAME
          OR SET SHELL VAR "GFORGE_USERNAME" TO YOUR GFORGE ACCOUNT NAME"""

    homepage = "https://gforge.inria.fr/projects/aerosol-p/"

    try:
        username = os.environ['GFORGE_USERNAME']
    except KeyError:
        username = getpass.getuser()

    version('trunk',    svn='https://scm.gforge.inria.fr/authscm/' + username + '/svn/aerosol-p/trunk')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('papi', default=False, description='Enable PAPI usage')
    variant('hdf5', default=True, description='Enable IO using parallel HDF5')
    variant('umfpack', default=True, description='Enable UMFPACK linear solver')
    variant('petsc', default=True, description='Enable PETSc linear solvers')
    variant('mumps', default=False, description='Enable MUMPS linear solver')
    variant('pastix', default=False, description='Enable PaStix linear solver')

    # required dependencies
    depends_on('cmake')
    depends_on('libxml2')
    depends_on('mpi')
    depends_on('blas')
    depends_on('lapack')
    depends_on('pampa@trunk')
    depends_on('scotch@6.0.3~pthread')

    # optional dependencies
    depends_on('papi', when="+papi")
    depends_on('hdf5+mpi', when="+hdf5")
    depends_on('suitesparse', when="+umfpack")
    depends_on('petsc@3.3+hypre~mumps~superlu-dist', when="+petsc")
    depends_on('mumps+scotch+ptscotch+metis+parmetis', when="+mumps")
    depends_on('pastix~metis', when="+pastix")

    parallel = False # parallel builds might require too much RAM (ie >8gb for 4c)

    def install(self, spec, prefix):
        with working_dir('aerosolBuild', create=True):
            # configure
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DWITH_XML2=True"])
            if spec.satisfies('+papi'):
                cmake_args.extend(["-DWITH_PAPI=True"])
            if spec.satisfies('+hdf5'):
                cmake_args.extend(["-DWITH_HDF5=True"])
            # configure dense linear solver
            cmake_args.extend(['-DBLAS_DIR=%s' % spec['blas'].prefix])
            cmake_args.extend(['-DLAPACK_DIR=%s' % spec['lapack'].prefix])
            if 'eigen-blas' in spec:
                cmake_args.extend(["-DLINEAR_ALGEBRA_PACKAGE=EIGENBLAS"])
            elif 'mkl' in spec:
                cmake_args.extend(["-DLINEAR_ALGEBRA_PACKAGE=MKL"])
            elif 'openblas' in spec:
                cmake_args.extend(["-DLINEAR_ALGEBRA_PACKAGE=OPENBLAS"])
            elif 'netlib' in spec or 'netlib-blas' in spec:
                cmake_args.extend(["-DLINEAR_ALGEBRA_PACKAGE=NETLIBBLAS"])
            else:
                cmake_args.extend(["-DLINEAR_ALGEBRA_PACKAGE=NOTHING"])
            # configure sparse linear solvers
            cmake_args.extend(["-DWITH_BLOCKDIAGONALSOLVER=True"])
            cmake_args.extend(["-DWITH_DIAGONALSOLVER=True"])
            if spec.satisfies('+umfpack'):
                cmake_args.extend(["-DWITH_UMFPACK=True"])
            if spec.satisfies('+petsc'):
                cmake_args.extend(["-DWITH_PETSC=True"])
                if spec.satisfies('+petsc+hypre'):
                    cmake_args.extend(["-DWITH_PETSC_HYPRE=True"])
            if spec.satisfies('+mumps'):
                cmake_args.extend(["-DWITH_MUMPS=True"])
            if spec.satisfies('+pastix'):
                cmake_args.extend(["-DWITH_PASTIX=True"])
            cmake(*cmake_args)

            # build
            make()

            #install
            make("install")

    # to use the existing version available in the environment: AEROSOL_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('AEROSOL_DIR'):
            aerosolroot=os.environ['AEROSOL_DIR']
            if os.path.isdir(aerosolroot):
                os.symlink(aerosolroot+"/bin", prefix.bin)
                os.symlink(aerosolroot+"/include", prefix.include)
                os.symlink(aerosolroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(aerosolroot+' directory does not exist.'+' Do you really have openmpi installed in '+aerosolroot+' ?')
        else:
            raise RuntimeError('AEROSOL_DIR is not set, you must set this environment variable to the installation path of your aerosol')
