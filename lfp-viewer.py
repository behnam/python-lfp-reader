#!/usr/bin/env python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://code.behnam.es/python-lfp-reader/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012-2013  Behnam Esfahbod


"""View LFP Picture files with refocus and edof/parallax support
"""


from __future__ import print_function

import os.path
import sys
import argparse

from lfp_reader.tk_lfp_viewer import TkLfpViewer
from lfp_reader import lfp_logging
lfp_logging.set_log_stream(sys.stdout)


DEBUG = False
QUIET = False


def view(file_dir_paths, **null):
    """Create a viewer window and show files
    """
    lfp_paths = []
    for x in file_dir_paths:
        if os.path.isdir(x):
            lfp_paths.extend(os.path.join(x, y) for y in os.listdir(x)
                    if os.path.isfile(os.path.join(x, y))
                    and os.path.join(x, y).lower().endswith('-stk.lfp'))
        else:
            lfp_paths.append(x)
    viewer = TkLfpViewer(lfp_paths)
    viewer.mainloop()


def main(argv=sys.argv[1:]):
    """Parse command-line arguments and call commands
    """
    global DEBUG, QUIET

    debug_kwargs = dict(
            action='store_true',
            help="Print debugging information on error",
            )
    quiet_kwargs = dict(
            action='store_true',
            help="Do not write anything to standard output",
            )
    lfp_file_kwargs = dict(
            metavar='picture-stk.lfp',
            help='LFP Picture (stk) file path',
            )

    # Main command
    p_main = argparse.ArgumentParser(description=__doc__)
    p_main.set_defaults(subcmd=view)
    p_main.add_argument('-d', '--debug', **debug_kwargs)
    p_main.add_argument('-q', '--quiet', **quiet_kwargs)
    p_main.add_argument('file_dir_paths', nargs='+', **lfp_file_kwargs)

    # Parse arguments
    try:
        args = p_main.parse_args(argv)
    except SystemExit:
        print()
        if 'info' in argv:
            p_info.print_help()
        elif 'export' in argv:
            p_export.print_help()
        else:
            p_main.print_help()
        sys.exit(2)

    # Run subcommand
    DEBUG = args.debug
    QUIET = args.quiet
    args.subcmd(**dict(args._get_kwargs()))


if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(3)
    except Exception as err:
        if DEBUG:
            raise
        else:
            if not QUIET:
                print("%s: error: %s" % (os.path.basename(sys.argv[0]), err), file=sys.stderr)
            sys.exit(9)

