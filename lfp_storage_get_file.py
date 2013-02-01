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


"""Write the content of a LFP Storage embedded file to standard output
"""


import os.path
import sys

from lfp_reader import LfpStorageFile


def main(lfp_path, emb_path):
    lfp = LfpStorageFile(lfp_path).load()
    try:
        chunk = lfp.files[emb_path]
    except:
        raise Exception("Cannot find embedded file `%s' in LFP Storrage file `%s'" % (emb_path, lfp_path))
    sys.stdout.write(chunk.data)


def usage(errcode=0, of=sys.stderr):
    print >>of, ("Usage: %s storage.lfp [storage-2.lfp]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)


if __name__=='__main__':
    if len(sys.argv) != 3:
        usage(1)
    try:
        main(*sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(2)
    except Exception as err:
        print >>sys.stderr, "Error:", err
        if sys.platform == 'win32': raw_input()
        sys.exit(9)

