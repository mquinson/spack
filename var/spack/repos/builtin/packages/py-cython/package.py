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

class PyCython(Package):
    """The Cython compiler for writing C extensions for the Python language."""
    homepage = "https://pypi.python.org/pypi/cython"


    version('0.27.2', '64abe5847736eb413a525b70b48afd7f',
    url='https://pypi.python.org/packages/98/bb/cd2be435e28ee1206151793a528028e3dc9a787fe525049efb73637f52bb/Cython-0.27.2.tar.gz')
    version('0.23.5', '66b62989a67c55af016c916da36e7514',
            url='https://pypi.python.org/packages/source/C/Cython/Cython-0.23.5.tar.gz')
    version('0.23.4', '157df1f69bcec6b56fd97e0f2e057f6e',
            url='https://pypi.python.org/packages/source/C/Cython/Cython-0.23.4.tar.gz')

    extends('python')

    def install(self, spec, prefix):
        python('setup.py', 'install', '--prefix=%s' % prefix)
