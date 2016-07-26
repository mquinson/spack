##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License (as
# published by the Free Software Foundation) version 2.1, February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
from spack import *
import os, sys, glob
import spack

class Mumps(Package):
    """MUMPS: a MUltifrontal Massively Parallel sparse direct Solver"""
    homepage = "http://mumps.enseeiht.fr"

    version('4.10.0', '959e9981b606cd574f713b8422ef0d9f',
            url="http://mumps.enseeiht.fr/MUMPS_4.10.0.tar.gz")
    version('5.0.0', '3c6aeab847e9d775ca160194a9db2b75',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.0.tar.gz")
    version('5.0.1', 'b477573fdcc87babe861f62316833db0',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.1.tar.gz")
    version('5.0.2', '591bcb2c205dcb0283872608cdf04927',
            url="http://mumps.enseeiht.fr/MUMPS_5.0.2.tar.gz")

    pkg_dir = spack.repo.dirname_for_package_name("fake")
    # fake tarball because we consider it is already installed
    version('exist', '7b878b76545ef9ddb6f2b61d4c4be833',
        url = "file:"+join_path(pkg_dir, "empty.tar.gz"))
    version('src')

    variant('blasmt', default=False, description='Enable Multithreaded Blas/Lapack if providen by the vendor')
    variant('mpi', default=True, description='Sequential version (no MPI)')
    variant('scotch', default=True, description='Enable Scotch')
    variant('ptscotch', default=False, description='Enable PT-Scotch')
    variant('metis', default=False, description='Enable Metis')
    variant('parmetis', default=False, description='Activate Parmetis as a possible ordering library')
    variant('double', default=True, description='Activate the compilation of dmumps')
    variant('float', default=True, description='Activate the compilation of smumps')
    variant('complex', default=True, description='Activate the compilation of cmumps and/or zmumps')
    variant('idx64', default=False, description='Use int64_t/integer*8 as default index type')
    variant('shared', default=True, description='Build MUMPS as a shared library')
    variant('examples', default=True, description='Enable compilation and installation of example executables')


    depends_on('scotch + esmumps', when='~ptscotch+scotch')
    depends_on('scotch + esmumps + mpi', when='+ptscotch')
    depends_on('scotch + idx64', when='+scotch+idx64')
    depends_on('scotch + idx64', when='+ptscotch+idx64')
    depends_on('metis + idx64', when='+metis+idx64')
    depends_on('metis + idx64', when='+parmetis+idx64')
    depends_on("metis@5:", when='@src+metis')
    depends_on("metis@5:", when='@5:+metis')
    depends_on("metis@:4", when='@4+metis')
    depends_on('parmetis', when="+parmetis")
    depends_on('blas')
    depends_on('lapack')
    depends_on('scalapack', when='+mpi')
    depends_on('mpi', when='+mpi')

    # this function is not a patch function because in case scalapack
    # is needed it uses self.spec['scalapack'].cc_link set by the
    # setup_dependent_environment in scalapack. This happen after patch
    # end before install
    # def patch(self):
    def write_makefile_inc(self):
        spec = self.spec
        if ('+parmetis' in spec or '+ptscotch' in spec) and '+mpi' not in spec:
            raise RuntimeError('You cannot use the variants parmetis or ptscotch without mpi')
        if (
            ( spec.satisfies('+metis')    and spec.satisfies('+scotch')   ) or
            ( spec.satisfies('+metis')    and spec.satisfies('+ptscotch') ) or
            ( spec.satisfies('+parmetis') and spec.satisfies('+scotch')   ) or
            ( spec.satisfies('+parmetis') and spec.satisfies('+ptscotch') )
           ):
            raise RuntimeError('You cannot use Metis and Scotch at the same'
             ' time because they are incompatible (Scotch provides a metis.h'
             ' which is not the same as the one providen by Metis)')

        blas_libs = spec['blas'].fc_link
        if spec.satisfies('+blasmt'):
            if '^mkl' in spec or '^essl' in spec or '^openblas+mt' in spec:
                blas_libs = spec['blas'].fc_link_mt
            else:
                raise RuntimeError('Only ^openblas+mt, ^mkl and ^essl provide multithreaded blas.')
        makefile_conf = ["LIBBLAS = %s" % blas_libs]
        lapack_libs = spec['lapack'].fc_link
        if spec.satisfies('+blasmt'):
            if '^mkl' in spec or '^essl' in spec:
                lapack_libs = spec['lapack'].fc_link_mt

        orderings = ['-Dpord']

        if '+ptscotch' in spec or '+scotch' in spec:
            join_lib = ' -l%s' % ('pt' if '+ptscotch' in spec else '')
            makefile_conf.extend(
                ["ISCOTCH = -I%s" % spec['scotch'].prefix.include,
                 "LSCOTCH = %s" % spec['scotch'].cc_link])
            orderings.append('-Dscotch')
            if '+ptscotch' in spec:
                orderings.append('-Dptscotch')

        if '+parmetis' in spec and '+metis' in spec:
            libname = 'parmetis' if '+parmetis' in spec else 'metis'
            makefile_conf.extend(
                ["IMETIS = -I%s -I%s" % (spec['metis'].prefix.include, spec['parmetis'].prefix.include),
                 "LMETIS = -L%s -l%s -L%s -l%s" % (spec['parmetis'].prefix.lib, 'parmetis',spec['metis'].prefix.lib, 'metis')])

            orderings.append('-Dparmetis')
        elif '+metis' in spec:
            makefile_conf.extend(
                ["IMETIS = -I%s" % spec['metis'].prefix.include,
                 "LMETIS = -L%s -l%s" % (spec['metis'].prefix.lib, 'metis')])

            orderings.append('-Dmetis')

        makefile_conf.append("ORDERINGSF = %s" % (' '.join(orderings)))

        # when building shared libs need -fPIC, otherwise
        # /usr/bin/ld: graph.o: relocation R_X86_64_32 against `.rodata.str1.1' can not be used when making a shared object; recompile with -fPIC
        fpic = '-fPIC' if '+shared' in spec else ''
        nofor_main = ''
        if spec.satisfies('%intel'):
            nofor_main = '-nofor_main'
        # TODO: test this part, it needs a full blas, scalapack and
        # partitionning environment with 64bit integers
        if '+idx64' in spec:
            makefile_conf.extend(
                # the fortran compilation flags most probably are
                # working only for intel and gnu compilers this is
                # perhaps something the compiler should provide
                ['OPTF    = %s -O  -DALLOW_NON_INIT %s %s' % (fpic,'-fdefault-integer-8' if self.compiler.name == "gcc" else '-i8',nofor_main),
                 'OPTL    = %s -O %s' % (fpic,nofor_main),
                 'OPTC    = %s -O -DINTSIZE64' % fpic])
        else:
            makefile_conf.extend(
                ['OPTF    = %s -O  -DALLOW_NON_INIT %s' % (fpic,nofor_main),
                 'OPTL    = %s -O %s' % (fpic,nofor_main),
                 'OPTC    = %s -O ' % fpic])


        if '+mpi' in spec:
            makefile_conf.extend(
                ["CC = %s" % spec['mpi'].mpicc,
                 "FC = %s" % spec['mpi'].mpifc,
                 "FL = %s" % spec['mpi'].mpifc,
                 "SCALAP = %s %s %s %s" % (spec['scalapack'].cc_link, spec['blacs'].cc_link, lapack_libs, blas_libs),
                 "MUMPS_TYPE = par"])
        else:
            makefile_conf.extend(
                ["CC = cc",
                 "FC = fc",
                 "FL = fc",
                 "MUMPS_TYPE = seq"])

        # TODO: change the value to the correct one according to the
        # compiler possible values are -DAdd_, -DAdd__ and/or -DUPPER
        makefile_conf.append("CDEFS   = -DAdd_")

        if '+shared' in spec:
            if sys.platform == 'darwin':
                # Building dylibs with mpif90 causes segfaults on 10.8 and 10.10. Use gfortran. (Homebrew)
                makefile_conf.extend([
                    'LIBEXT=.dylib',
                    'AR=%s -dynamiclib -Wl,-install_name -Wl,%s/$(notdir $@) -undefined dynamic_lookup -o ' % (os.environ['FC'],prefix.lib),
                    'RANLIB=echo'
                ])
            else:
                makefile_conf.extend([
                    'LIBEXT=.so',
                    'AR=$(FL) -shared -Wl,-soname -Wl,%s/$(notdir $@) -o' % prefix.lib,
                    'RANLIB=echo'
                ])
        else:
            makefile_conf.extend([
                'LIBEXT  = .a',
                'AR = ar vr',
                'RANLIB = ranlib'
            ])

        makefile_inc_template = join_path(os.path.dirname(self.module.__file__),
                                          'Makefile.inc')
        with open(makefile_inc_template, "r") as fh:
            makefile_conf.extend(fh.read().split('\n'))

        with working_dir('.'):
            with open("Makefile.inc", "w") as fh:
                makefile_inc = '\n'.join(makefile_conf)
                fh.write(makefile_inc)


    def install(self, spec, prefix):
        make_libs = []

        # the choice to compile ?examples is to have kind of a sanity
        # check on the libraries generated.
        if '+float' in spec:
            make_libs.append('sexamples')
            if '+complex' in spec:
                make_libs.append('cexamples')

        if '+double' in spec:
            make_libs.append('dexamples')
            if '+complex' in spec:
                make_libs.append('zexamples')

        self.write_makefile_inc()

        # Build fails in parallel
        make(*make_libs, parallel=False)

        install_tree('lib', prefix.lib)
        install_tree('include', prefix.include)

        if '~mpi' in spec:
            lib_dsuffix = '.dylib' if sys.platform == 'darwin' else '.so'
            lib_suffix = lib_dsuffix if '+shared' in spec else '.a'
            install('libseq/libmpiseq%s' % lib_suffix, prefix.lib)
            for f in glob.glob(join_path('libseq','*.h')):
                install(f, prefix.include)

        # FIXME: extend the tests to mpirun -np 2 (or alike) when build with MPI
        # FIXME: use something like numdiff to compare blessed output with the current
        with working_dir('examples'):
            if '+float' in spec:
                os.system('./ssimpletest < input_simpletest_real')
                if '+complex' in spec:
                    os.system('./csimpletest < input_simpletest_real')
            if '+double' in spec:
                os.system('./dsimpletest < input_simpletest_real')
                if '+complex' in spec:
                    os.system('./zsimpletest < input_simpletest_cmplx')

    def setup_dependent_package(self, module, dep_spec):
        """Dependencies of this package will get the link for Mumps."""
        spec = self.spec
        ## mumps libraries
        spec.fc_link = '-L%s' % spec.prefix.lib
        for l in ["smumps", "dmumps", "cmumps", "zmumps", "mumps_common", "pord"]:
            spec.fc_link  += ' -l%s' % l
        if spec.satisfies('~mpi'):
            # mumps libmpiseq provides dummy symbols for MPI and ScaLAPACK
            # be aware that it must come after the actual MPI library during the link phase
            spec.fc_link  += ' -lmpiseq'
        ## mumps dependencies
#         if spec.satisfies('+metis'):
#             # metis
#             spec.fc_link += ' '+spec['metis'].cc_link
#         if spec.satisfies('+parmetis'):
#             # parmetis
#             spec.fc_link += ' '+spec['parmetis'].cc_link
#         if spec.satisfies('+scotch'):
#             # scotch and ptscotch
#             spec.fc_link += ' '+spec['scotch'].cc_link
#         # scalapack, blacs
#         spec.fc_link += ' %s %s' % (spec['scalapack'].cc_link, spec['blacs'].cc_link)
#         if spec.satisfies('+blasmt'):
#             # lapack and blas
#             if '^mkl' in spec or '^essl' in spec:
#                 spec.fc_link += ' %s' % spec['lapack'].fc_link_mt
#             else:
#                 spec.fc_link += ' %s' % spec['lapack'].fc_link
#             spec.fc_link += ' %s' % spec['blas'].fc_link_mt
#         else:
#             spec.fc_link += ' %s %s' % (spec['lapack'].fc_link, spec['blas'].fc_link)

        # there is a bug with the hash calculation of mumps
        spec.mumpsprefix=spec.prefix
