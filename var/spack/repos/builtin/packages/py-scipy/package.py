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

class PyScipy(Package):
    """Scientific Library for Python."""
    homepage = "http://www.scipy.org/"
    url      = "https://pypi.python.org/packages/source/s/scipy/scipy-0.15.0.tar.gz"

    version('0.17.0', '5ff2971e1ce90e762c59d2cd84837224')
    version('0.15.1', 'be56cd8e60591d6332aac792a5880110')
    version('0.15.0', '639112f077f0aeb6d80718dc5019dc7a')

    extends('python')
    depends_on('py-nose')
    depends_on('py-numpy+blas+lapack')
    depends_on('blas')
    depends_on('lapack')

    def install(self, spec, prefix):
        # restrict to a blas that contains cblas symbols
        if 'openblas+lapack' in spec:
            with open('site.cfg', 'w') as f:
                f.write('[DEFAULT]\n')
                f.write('library_dirs=%s\n' % spec['blas'].prefix.lib)
        #elif 'mkl' in spec:
        #    with open('site.cfg', 'w') as f:
        #        f.write('[mkl]\n')
        #        f.write('library_dirs=%s\n' % spec['blas'].prefix.lib)
        #        f.write('include_dirs=%s\n' % spec['blas'].prefix.include)
        #        f.write('mkl_libs=mkl_intel_lp64,mkl_intel_thread,mkl_core')
        else:
            raise RuntimeError('py-numpy blas/lapack must be one of: openblas+lapack')

        python('setup.py', 'install', '--prefix=%s' % prefix)
