from spack import *
import os
from subprocess import call
import spack

class Magma(Package):
    """a dense linear algebra library similar to LAPACK but for heterogeneous/hybrid architectures"""
    homepage = "http://icl.cs.utk.edu/magma/index.html"

    version('2.0.1', '6732465e13d88419a77cb5f8ccecd1fb',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-2.0.1.tar.gz")
    version('1.7.0-b', '19795d41ec15531e7b69a41a52b5fa74',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.7.0-b.tar.gz")
    version('1.6.2', 'ba22d397a28a957c090b43ba895cb735',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.6.2.tar.gz")
    version('1.6.1', 'ae0fe7fefe2f27847b2f5a48b6fab429',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.6.1.tar.gz")
    version('1.6.0', '10c01eec8763878c85abb83274f65426',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.6.0.tar.gz")
    version('1.5.0', '18074e2e5244924730063fe0f694abca',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.5.0.tar.gz")
    version('1.4.1', '19af5b2a682f43049ed3318cb341cf88',
            url="http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-1.4.1.tar.gz")

    variant('debug',  default=False, description='add -g symbol')

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
            url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    depends_on("cuda")
    depends_on("blas")
    depends_on("lapack")
    depends_on("cblas")

    def setup(self):

        spec = self.spec
        pkg_dir = spack.repo.dirname_for_package_name("magma")
        call(["cp", pkg_dir+"/make.inc.mkl-gcc", "."])
        call(["ln", "-s", "make.inc.mkl-gcc", "make.inc"])
        mf = FileFilter('make.inc')

        mf.filter('CC        = gcc',      'CC        = cc')
        mf.filter('CXX       = g\+\+',    'CXX       = c++')
        mf.filter('FORT      = gfortran', 'FORT      = f90')

        if spec.satisfies("+debug"):
            mf.filter('-O3', '-O2 -g')

        if spec.satisfies("%intel"):
            mf.filter('^CFLAGS.*',   'CFLAGS   = -O3 $(FPIC) -DADD_ -Wall -Wshadow -openmp')
            mf.filter('^FFLAGS.*',   'FFLAGS   = -O3 $(FPIC) -DADD_ -warn all -warn nounused -nogen-interfaces')
            mf.filter('^F90FLAGS.*', 'F90FLAGS = -O3 $(FPIC) -DADD_ -warn all -warn nounused')
            mf.filter('^LDFLAGS.*',  'LDFLAGS  =     $(FPIC) -openmp')
        elif spec.satisfies("%xl"):
            mf.filter('^CFLAGS.*',    'CFLAGS    = -O3 -qpic')
            mf.filter('^FFLAGS.*',    'FFLAGS    = -O3 -qpic')
            mf.filter('^F90FLAGS.*',  'F90FLAGS  = -O3 -qpic')
            mf.filter('^NVCCFLAGS.*', 'NVCCFLAGS = -O3 -Xcompiler \"-fno-strict-aliasing $(FPIC)\"')
            mf.filter('^LDFLAGS.*',  'LDFLAGS  =')


        if not '^mkl' in spec:
            mf.filter('-DMAGMA_WITH_MKL', '')
            mf.filter('-include make.check-mkl', '')

        blas_libs = spec['blas'].fc_link
        cblas_libs = spec['cblas'].fc_link
        lapack_libs = spec['lapack'].fc_link
        cpu_kernels = lapack_libs+' '+cblas_libs+' '+blas_libs
        cuda_libs = ' -lcusparse -lcublas -lcudart'
        lib_list = cpu_kernels+cuda_libs+' -lstdc++'
        if spec.satisfies('%gcc') and not '^mkl' in spec:
            lib_list += ' -lgfortran'
        mf.filter('^LIB       =.*', 'LIB       = %s' % lib_list)

        if spec.satisfies("%xl"):
            mf = FileFilter('Makefile')
            mf.filter('-Dmagma_devptr_t', '-WF,-Dmagma_devptr_t')


    def install(self, spec, prefix):

        self.setup()

        if spec.satisfies('@2:'):
            make()
            call(["make", "install", "prefix=%s" % prefix])
        else:
            # before 2. versions, some examples was not compiling so
            # that we ignore errors because we just want to install
            # the libs and headers
            make("-i")
            call(["make", "--ignore-errors", "install", "prefix=%s" % prefix])

    # to use the existing version available in the environment: MAGMA_DIR environment variable must be set
    @when('@exist')
    def install(self, spec, prefix):
        if os.getenv('MAGMA_DIR'):
            magmaroot=os.environ['MAGMA_DIR']
            if os.path.isdir(magmaroot):
                os.symlink(magmaroot+"/bin", prefix.bin)
                os.symlink(magmaroot+"/include", prefix.include)
                os.symlink(magmaroot+"/lib", prefix.lib)
            else:
                raise RuntimeError(magmaroot+' directory does not exist.'+' Do you really have openmpi installed in '+magmaroot+' ?')
        else:
            raise RuntimeError('MAGMA_DIR is not set, you must set this environment variable to the installation path of your magma')
