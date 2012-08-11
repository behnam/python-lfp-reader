#!/usr/bin/env python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://behnam.github.com/python-lfp-reader/
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
# Copyright (C) 2012  Behnam Esfahbod


"""Export LFP Storage file into separate data files
"""


import os.path
import sys

from lfp_reader import LfpStorageFile


def usage(errcode=0, of=sys.stderr):
    print ("Usage: %s storage_file.lfp [embedded-file-path]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)

if __name__=='__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    lfp_path = sys.argv[1]
    exp_path = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        lfp = LfpStorageFile(lfp_path).load()

        if not exp_path:
            # Export all files
            lfp.export()

        else:
            # Write the content of one embedded file to standard output
            try:
                exp_chunk = lfp.files[exp_path]
            except:
                raise Exception("Cannot find embedded file `%s` in LFP Storrage file %s"
                        % (exp_path, lfp_path))
            sys.stdout.write(exp_chunk.data)

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

