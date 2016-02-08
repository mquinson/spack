from spack import *
import spack

class Parmetis(Package):
    """ParMETIS is an MPI-based parallel library that implements a
       variety of algorithms for partitioning unstructured graphs,
       meshes, and for computing fill-reducing orderings of sparse
       matrices."""
    homepage = "http://glaros.dtc.umn.edu/gkhome/metis/parmetis/overview"

    version('4.0.3', 'f69c479586bf6bb7aff6a9bc0c739628',
            url="http://glaros.dtc.umn.edu/gkhome/fetch/sw/parmetis/parmetis-4.0.3.tar.gz")

    pkg_dir = spack.db.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on('cmake')
    depends_on('mpi')

    def install(self, spec, prefix):
        cmake_args = ["."]
        cmake_args.extend(std_cmake_args)
        mpi = spec['mpi'].prefix
        try:
            mpicc = binmpicc
        except NameError:
            mpicc = 'mpicc'
        try:
            mpicxx = binmpicxx
        except NameError:
            mpicxx = 'mpic++'
        cmake_args+=[
              '-DGKLIB_PATH=%s/metis/GKlib' % pwd(),
              '-DMETIS_PATH=%s/metis' % pwd(),
              '-DSHARED=1',
              '-DCMAKE_C_COMPILER=%s' % mpicc,
              '-DCMAKE_CXX_COMPILER=%s' % mpicxx,
              '-DSHARED=1']
        cmake(*cmake_args)

        make()
        make("install")

    # to use the existing version available in the environment: PARMETIS_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('PARMETIS_DIR'):
            parmetisroot=os.environ['PARMETIS_DIR']
            if os.path.isdir(parmetisroot):
                os.symlink(parmetisroot+"/bin", prefix.bin)
                os.symlink(parmetisroot+"/include", prefix.include)
                os.symlink(parmetisroot+"/lib", prefix.lib)
            else:
                sys.exit(parmetisroot+' directory does not exist.'+' Do you really have openmpi installed in '+parmetisroot+' ?')
        else:
            sys.exit('PARMETIS_DIR is not set, you must set this environment variable to the installation path of your parmetis')
