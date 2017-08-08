##############################################################################
# Copyright (c) 2013-2016, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Created by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the NOTICE and LICENSE files for our notice and the LGPL.
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
import os
from subprocess import call

class Fxt(Package):
    """This library provides efficient support for recording traces"""
    homepage = "http://savannah.nongnu.org/projects/fkt"

    version('0.3.3' , '52055550a21655a30f0381e618081776',
            url      = "http://download.savannah.gnu.org/releases/fkt/fxt-0.3.3.tar.gz")

    variant('moreparams', default=False, description='Increase the value of FXT_MAX_PARAMS (to allow longer task names).')

    def install(self, spec, prefix):

        if spec.satisfies("arch=linux-ppc64le"):
            pkg_dir = spack.repo.dirname_for_package_name("fxt")
            call(["cp", pkg_dir+"/config.guess", "."])

        os.environ["CFLAGS"] = "-fPIC"
        configure("--prefix=%s" % prefix)

        # Increase the value of FXT_MAX_PARAMS (to allow longer task names)
        if '+moreparams' in spec:
            mf = FileFilter('tools/fxt.h')
            mf.filter('#define FXT_MAX_PARAMS.*', '#define FXT_MAX_PARAMS 16')

        make(parallel=False)
        # The mkdir commands in fxt's install can fail in parallel
        make("install", parallel=False)
