#!/usr/bin/env python

# todo license
# todo copyright


"""LFP (Light Field Photography) Generic File Reader
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

