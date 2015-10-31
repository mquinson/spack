from spack import *
import os

class Plasma(Package):
    """Parallel Linear Algebra for Scalable Multi-core Architectures."""
    homepage = "http://icl.cs.utk.edu/plasma/"
    url      = "http://icl.cs.utk.edu/projectsfiles/plasma/pubs/plasma_2.7.1.tar.gz"

    version('2.7.1', 'c3deb85ccf10e6eaac9f0ba663702805')
    version('2.7.0', '8fcdfaf36832ab98e59b8299263999ca')

    depends_on("hwloc")
    depends_on("cblas")
    depends_on("blas")
    depends_on("lapack")
    depends_on("netlib-lapacke")

    def setup(self):
        if not os.path.isfile('make.inc'):
            os.symlink('make.inc.example', 'make.inc')
        mf = FileFilter('make.inc')
        spec = self.spec

        mf.filter('^CC        =.*', 'prefix=%s\n\nCC        = cc' % self.prefix)
        mf.filter('^FC        =.*', 'FC        = f90')
        mf.filter('^LOADER    =.*', 'LOADER    = f90')

        if spec.satisfies('%gcc'):
            mf.filter('LDFLAGS   = -O2 -nofor_main', 'LDFLAGS   = -O2')
            mf.filter('FFLAGS    = -O2 -fltconsistency -fp_port', 'FFLAGS    = -O2')

        if spec.satisfies('^netlib-blas'):
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_')
        elif spec.satisfies('^mkl-blas'):
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -m64 -I${MKLROOT}/include')
            else:
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -diag-disable vec -m64 -I${MKLROOT}/include')

        blas = spec['blas'].prefix
        blas_libs = " ".join(blaslibname)
        if spec.satisfies('^netlib-blas'):
            if spec.satisfies('%gcc'):
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lgfortran' % blas.lib)
            else:
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lifort' % blas.lib)
        elif spec.satisfies('^mkl-blas'):
            mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = %s' % blas_libs)

        cblas = spec['cblas'].prefix
        cblas_libs = " ".join(cblaslibname)
        if spec.satisfies('^netlib-cblas'):
            mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = -L%s -lcblas' % cblas.lib)
        elif spec.satisfies('^mkl-cblas'):
            mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = %s' % cblas_libs)

        lapack = spec['lapack'].prefix
        lapack_libs = " ".join(lapacklibname)
        if spec.satisfies('^netlib-lapack'):
            mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = -L%s -ltmglib -llapack' % lapack.lib)
        elif spec.satisfies('^mkl-lapack'):
            mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = %s' % lapack_libs)

        lapacke = spec['netlib-lapacke'].prefix
        mf.filter('^INCCLAPACK  =.*', 'INCCLAPACK  = -I%s' % lapacke.include)
        mf.filter('^LIBCLAPACK  =.*', 'LIBCLAPACK  = -L%s -llapacke' % lapacke.lib)

    def install(self, spec, prefix):

        self.setup()
        make()
        make("install")
        # examples are not installed by default
        install_tree('testing', '%s/lib/plasma/testing' % prefix)
        install_tree('timing', '%s/lib/plasma/timing' % prefix)
