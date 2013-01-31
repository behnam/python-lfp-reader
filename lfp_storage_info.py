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


"""Show information about LFP Storage file
"""


import os.path
import sys

from lfp_reader import LfpStorageFile


def usage(errcode=0, of=sys.stderr):
    print ("Usage: %s storage_file.lfp" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)

if __name__=='__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        usage()
    lfp_path = sys.argv[1]

    try:
        lfp = LfpStorageFile(lfp_path).load()
        for path, chunk in lfp.files_sorted:
            print "%12d\t%s" % (chunk.size, path)

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

