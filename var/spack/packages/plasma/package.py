from spack import *
import os

class Plasma(Package):
    """Parallel Linear Algebra for Scalable Multi-core Architectures."""
    homepage = "http://icl.cs.utk.edu/plasma/"
    url      = "http://icl.cs.utk.edu/projectsfiles/plasma/pubs/plasma_2.7.1.tar.gz"

    version('2.7.1', 'c3deb85ccf10e6eaac9f0ba663702805')
    version('2.7.0', '8fcdfaf36832ab98e59b8299263999ca')

    variant('mkl', default=False, description='Use BLAS/LAPACK from the Intel MKL library')

    depends_on("hwloc")
    depends_on("cblas", when='~mkl')
    depends_on("blas", when='~mkl')
    depends_on("lapack+lapacke")

    def patch(self):
        os.symlink('make.inc.example', 'make.inc')
        mf = FileFilter('make.inc')
        spec = self.spec

        mf.filter('^CC        =.*', 'prefix=%s\n\nCC        = cc' % self.prefix)
        mf.filter('^FC        =.*', 'FC        = f90')
        mf.filter('^LOADER    =.*', 'LOADER    = f90')

        if spec.satisfies('%gcc'):
            mf.filter('LDFLAGS   = -O2 -nofor_main', 'LDFLAGS   = -O2')
            mf.filter('FFLAGS    = -O2 -fltconsistency -fp_port', 'FFLAGS    = -O2')
        lapack = spec['lapack'].prefix
        mf.filter('^INCCLAPACK  =.*', 'INCCLAPACK  = -I%s' % lapack.include)
        mf.filter('^LIBCLAPACK  =.*', 'LIBCLAPACK  = -L%s -llapacke' % lapack.lib)

        if spec.satisfies('~mkl'):
            blas = spec['blas'].prefix
            cblas = spec['cblas'].prefix
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_')
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lgfortran' % blas.lib)
            else:
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lifort' % blas.lib)

            mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = -L%s -lcblas' % cblas.lib)
            mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = -L%s -ltmglib -llapack' % lapack.lib)

        else:
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -m64 -I${MKLROOT}/include')
            else:
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -diag-disable vec -m64 -I${MKLROOT}/include')
            mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -Wl,--no-as-needed -L${MKLROOT}/lib/intel64 -lmkl_intel_lp64 -lmkl_core -lmkl_sequential -lpthread -lm')
            mf.filter('^LIBCBLAS    =.*', '#LIBCBLAS    =')
            mf.filter('^LIBLAPACK   =.*', '#LIBLAPACK   =')

    def install(self, spec, prefix):

        make()
        make("install")
        # examples are not installed by default
        install_tree('testing', '%s/lib/plasma/testing' % prefix)
        install_tree('timing', '%s/lib/plasma/timing' % prefix)
