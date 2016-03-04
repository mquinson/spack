##############################################################################
# Copyright (c) 2013, Lawrence Livermore National Security, LLC.
# Produced at the Lawrence Livermore National Laboratory.
#
# This file is part of Spack.
# Written by Todd Gamblin, tgamblin@llnl.gov, All rights reserved.
# LLNL-CODE-647188
#
# For details, see https://github.com/llnl/spack
# Please also see the LICENSE file for our notice and the LGPL.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License (as published by
# the Free Software Foundation) version 2.1 dated February 1999.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the IMPLIED WARRANTY OF
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the terms and
# conditions of the GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##############################################################################
import sys
import argparse

import llnl.util.tty as tty

import spack
import spack.cmd
from spack.cmd.find import display_specs

description = "Build packages already staged"

def setup_parser(subparser):
    subparser.add_argument(
        '-a', '--all', action='store_true', dest='all',
        help="Build all matching packages.")
    subparser.add_argument(
        '-d', '--build-dependencies', action='store_true', dest='build_deps',
        help="Also build dependencies of requested packages.")
    subparser.add_argument(
        '-j', '--jobs', action='store', type=int,
        help="Explicitly set number of make jobs.  Default is #cpus.")
    subparser.add_argument(
        '-v', '--verbose', action='store_true', dest='verbose',
        help="Display verbose build output while building.")
    subparser.add_argument(
        'packages', nargs=argparse.REMAINDER, help="specs of packages to build")


def build(parser, args):
    if not args.packages:
        tty.die("build requires at least one package argument")

    if args.jobs is not None:
        if args.jobs <= 0:
            tty.die("The -j option must be a positive integer!")

    # TODO: make this an argument, not a global.
    spack.do_checksum = False

    with spack.installed_db.write_transaction():
        specs = spack.cmd.parse_specs(args.packages)

        # For each spec provided, make sure it refers to only one package.
        # Fail and ask user to be unambiguous if it doesn't
        pkgs = []
        for spec in specs:
            matching_specs = spack.installed_db.query(spec)
            if not args.all and len(matching_specs) > 1:
                tty.error("%s matches multiple packages:" % spec)
                print
                display_specs(matching_specs, long=True)
                print
                print "You can either:"
                print "  a) Use a more specific spec, or"
                print "  b) use spack build -a to build ALL matching specs."
                sys.exit(1)

            for s in matching_specs:
                try:
                    # should work if package is known to spack
                    pkgs.append(s.package)

                except spack.packages.UnknownPackageError, e:
                    # The package.py file has gone away -- but still want to
                    # uninstall.
                    spack.Package(s).install(force=True)

        # Sort packages to be built by the number of installed dependents
        def num_installed_deps(pkg):
            return len(pkg.installed_dependents)
        pkgs.sort(key=num_installed_deps)

        # Build packages in order now.
        for pkg in pkgs:
            pkg.do_build(
                build_deps=args.build_deps,
                make_jobs=args.jobs,
                verbose=args.verbose)
