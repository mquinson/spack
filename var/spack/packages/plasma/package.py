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
        force_symlink('make.inc.example', 'make.inc')
        mf = FileFilter('make.inc')
        spec = self.spec

        mf.filter('^CC        =.*', 'prefix=%s\n\nCC        = cc' % self.prefix)
        mf.filter('^FC        =.*', 'FC        = f90')
        mf.filter('^LOADER    =.*', 'LOADER    = f90')

        if spec.satisfies('%gcc'):
            mf.filter('LDFLAGS   = -O2 -nofor_main', 'LDFLAGS   = -O2')
            mf.filter('FFLAGS    = -O2 -fltconsistency -fp_port', 'FFLAGS    = -O2')

        if '^netlib-blas' in spec:
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_')
        elif '^mkl-blas' in spec:
            if spec.satisfies('%gcc'):
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -m64 -I${MKLROOT}/include')
            else:
                mf.filter('CFLAGS    = -O2 -DADD_ -diag-disable vec', 'CFLAGS    = -O2 -DADD_ -diag-disable vec -m64 -I${MKLROOT}/include')

        blas = spec['blas'].prefix
        blas_libs = " ".join(blaslibname)
        if '^netlib-blas' in spec:
            if spec.satisfies('%gcc'):
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lm' % blas.lib)
            else:
                mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = -L%s -lblas -lm' % blas.lib)
        elif '^mkl-blas' in spec:
            mf.filter('^LIBBLAS     =.*', 'LIBBLAS     = %s' % blas_libs)

        cblas = spec['cblas'].prefix
        cblas_libs = " ".join(cblaslibname)
        if '^netlib-cblas' in spec:
            mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = -L%s -lcblas' % cblas.lib)
        elif '^mkl-cblas' in spec:
            mf.filter('^LIBCBLAS    =.*', 'LIBCBLAS    = %s' % cblas_libs)

        lapack = spec['lapack'].prefix
        lapack_libs = " ".join(lapacklibname)
        tmg_libs = " ".join(tmglibname)
        if '^netlib-lapack' in spec:
            mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = -L%s -ltmglib -llapack' % lapack.lib)
        elif '^mkl-lapack' in spec:
            mf.filter('^LIBLAPACK   =.*', 'LIBLAPACK   = %s' % lapack_libs)

        lapacke = spec['netlib-lapacke'].prefix
        lapacke_libs = " ".join(lapackelibname)
        mf.filter('^INCCLAPACK  =.*', 'INCCLAPACK  = -I%s' % lapacke.include)
        if '^netlib-lapacke' in spec:
            mf.filter('^LIBCLAPACK  =.*', 'LIBCLAPACK  = -L%s -llapacke' % lapacke.lib)
        elif '^mkl-lapacke' in spec:
            mf.filter('^LIBCLAPACK  =.*', 'LIBCLAPACK  = %s' % lapacke_libs)

    def install(self, spec, prefix):

        self.setup()
        make()
        make("install")
        # examples are not installed by default
        install_tree('testing', '%s/lib/plasma/testing' % prefix)
        install_tree('timing', '%s/lib/plasma/timing' % prefix)
