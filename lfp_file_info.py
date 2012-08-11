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


"""Show information about LFP (Light Field Photography) file
"""


import os.path
import sys
import operator
import json

from lfp_reader import LfpGenericFile


def usage(errcode=0, of=sys.stderr):
    print ("Usage: %s file.lfp [chunk-sha1]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)

if __name__=='__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()
    lfp_path = sys.argv[1]
    sha1 = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        lfp = LfpGenericFile(lfp_path).load()

        # Write file metadata and list its data chunks
        if not sha1:
            print "Metadata:",
            print json.dumps(lfp.meta.content, indent=4)
            print
            print "Data Chunks: %d [" % len(lfp.chunks)
            for sha1, chunk in sorted(lfp.chunks.iteritems(), key=operator.itemgetter(0)):
                print "%12d\t%s" % (chunk.size, sha1)
            print "]"

        # Write the content of the chunk to standard output
        else:
            try:
                chunk = lfp.chunks[sha1]
            except:
                raise Exception("Cannot find chunk `%s` in LFP file" % sha1)
            sys.stdout.write(chunk.data)

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

