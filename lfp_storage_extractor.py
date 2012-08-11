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


"""Show information about LFP (Light Field Photography) Storage file
"""


import os.path
import sys
import operator


from lfp_reader import LfpStorageFile


def usage(errcode=0, of=sys.stderr):
    print ("Usage: %s storage_file.lfp [embedded-file-path]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)

if __name__=='__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    lfp_path = sys.argv[1]
    path = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        lfp = LfpStorageFile(lfp_path).load()

        # List embedded files
        if not path:
            for path, chunk in sorted(lfp.files.iteritems(), key=operator.itemgetter(1)):
                print "%12d\t%s" % (chunk.size, path)

        # Write the content of embedded file to standard output
        else:
            try:
                file_chunk = lfp.files[path]
            except:
                raise Exception("Cannot find file `%s` in LFP Storrage file" % path)
            sys.stdout.write(file_chunk.data)

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

