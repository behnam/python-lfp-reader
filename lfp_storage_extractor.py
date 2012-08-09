#!/usr/bin/env python

# todo license
# todo copyright


"""LFP (Light Field Photography) Storage File Reader
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

