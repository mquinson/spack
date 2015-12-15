from spack import *
import os
import getpass
import spack

class Aerosol(Package):
    """Aerosol is a high order Finite Volume C++ library. It requires an MPI
       implementation, Pampa (therefore also Scotch), BLAS or Eigen3/IMKL,
       libXML2 and can also utilize HDF5 and PAPI.
       
       As there is no publically released version of aerosol yet, this package
       requires the user has access to Aerosol's repository on gforge.
          PLEASE MAKE SURE YOUR USERNAME MATCHES YOUR GFORGE ACCOUNT NAME 
          OR SET SHELL VAR "GFORGE_USERNAME" TO YOUR GFORGE ACCOUNT NAME"""

    homepage = "https://gforge.inria.fr/projects/aerosol-p/"
    url      = "http://www.dontexist.com/aerosol-0.0.0.tar.gz"

    try:
        username = os.environ['GFORGE_USERNAME']
    except KeyError:
        username = getpass.getuser()

    version('svn-head', svn='https://scm.gforge.inria.fr/authscm/' + username + '/svn/aerosol-p/trunk')

    pkg_dir = spack.db.dirname_for_package_name("aerosol")

    variant('papi', default=True, description='Enable PAPI usage')
    variant('hdf5', default=True, description='Enable IO using parallel HDF5')

    depends_on('cmake')
    depends_on('mpi')
    depends_on('libxml2')
    depends_on('blas')
    depends_on('papi', when="+papi")
    depends_on('hdf5+mpi', when="+hdf5")

    parallel = False # parallel builds might require too much RAM (ie >8gb for 4c)

    def install(self, spec, prefix):
        with working_dir('aerosolBuild', create=True):
            # configure
            cmake_args = [".."]
            cmake_args.extend(std_cmake_args)
            cmake_args.extend(["-DWITH_BLOCKDIAGONALSOLVER=True"])
            cmake_args.extend(["-DWITH_DIAGONALSOLVER=True"])
#FIXME NIKOS add the rest of the lin solvers: MUMPS, UMFPACK, PETSC/PETSC-hypre
            cmake_args.extend(["-DWITH_XML2=True"])
            if spec.satisfies('+papi'):
                cmake_args.extend(["-DWITH_PAPI=True"])
            if spec.satisfies('+hdf5'):
                cmake_args.extend(["-DWITH_HDF5=True"])
#FIXME NIKOS            if spec['blas'] == eigen-blas:
#FIXME NIKOS                cmake_args.extend(["-DWITH_LINEAR_ALGEBRA_PACKAGE=EIGEN"])
#FIXME NIKOS            else if spec['blas'] == imkl:
#FIXME NIKOS                cmake_args.extend(["-DWITH_LINEAR_ALGEBRA_PACKAGE=IMKL"])
#FIXME NIKOS            else :
#FIXME NIKOS                cmake_args.extend(["-DWITH_LINEAR_ALGEBRA_PACKAGE=BLAS"])
            cmake(*cmake_args)

            # build
            make()

            #install
            make("install")
