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


"""Parse LFP Storage files and access embedded data
"""


from __future__ import print_function

import os.path
import sys
import argparse

from lfp_reader import LfpStorageFile, lfp_logging
lfp_logging.set_log_stream(sys.stdout)


DEBUG = False
QUIET = False


def info(lfp_files, **null):
    """Show information about LFP Storage file
    """
    for idx, lfp_file in enumerate(lfp_files):
        if not QUIET:
            if idx > 0: print()
            print("LFP Storage file: %s" % lfp_file.name)
        LfpStorageFile(lfp_file).load().print_info()



def export(lfp_files, **null):
    """Export LFP Storage file into separate data files
    """
    for idx, lfp_file in enumerate(lfp_files):
        if not QUIET:
            if idx > 0: print()
            print("LFP Storage file: %s" % lfp_file.name)
        LfpStorageFile(lfp_file).load().export()


def extract(lfp_file, emb_path, **null):
    """Extract the content of a LFP Storage embedded file
    """
    lfp = LfpStorageFile(lfp_file).load()
    try:
        chunk = lfp.files[emb_path]
    except:
        raise Exception("Cannot find embedded file `%s' in LFP Storage file `%s'" % (emb_path, lfp_file.name))
    sys.stdout.write(chunk.data.decode('UTF-8'))


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
            type=argparse.FileType(mode='rb'),
            metavar='storage.lfp',
            help='LFP Storage file path ("IMG_0001.lfp")',
            )

    # Main command
    p_main = argparse.ArgumentParser(description=__doc__)
    p_subs = p_main.add_subparsers(title='subcommands')

    # Info command
    p_info = p_subs.add_parser('info', help=info.__doc__)
    p_info.set_defaults(subcmd=info)
    p_info.add_argument('-d', '--debug', **debug_kwargs)
    p_info.add_argument('-q', '--quiet', **quiet_kwargs)
    p_info.add_argument('lfp_files', nargs='+', **lfp_file_kwargs)

    # Export command
    p_export = p_subs.add_parser('export', help=export.__doc__)
    p_export.set_defaults(subcmd=export)
    p_export.add_argument('-d', '--debug', **debug_kwargs)
    p_export.add_argument('-q', '--quiet', **quiet_kwargs)
    p_export.add_argument('lfp_files', nargs='+', **lfp_file_kwargs)

    # Extract command
    p_extract = p_subs.add_parser('extract', help=extract.__doc__)
    p_extract.set_defaults(subcmd=extract)
    p_extract.add_argument('-d', '--debug', **debug_kwargs)
    p_extract.add_argument('-q', '--quiet', **quiet_kwargs)
    p_extract.add_argument('lfp_file', **lfp_file_kwargs)
    p_extract.add_argument('emb_path',
            help=r"Path to embedded data file ('C:\...')")

    # Parse arguments
    try:
        args = p_main.parse_args(argv)
    except SystemExit:
        print()
        if 'info' in argv:
            p_info.print_help()
        elif 'export' in argv:
            p_export.print_help()
        elif 'extract' in argv:
            p_extract.print_help()
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

