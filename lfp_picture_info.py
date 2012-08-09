#!/usr/bin/env python

# todo license
# todo copyright


"""LFP (Light Field Photography) Picture File Reader
"""


import os.path
import sys

from lfp_reader import LfpPictureFile


def usage(errcode=0, of=sys.stderr):
    print ("Usage: %s picture-file.lfp" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)

if __name__=='__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        usage()
    lfp_path = sys.argv[1]


    try:
        lfp = LfpPictureFile(lfp_path).load()

        print
        print "Frame:"
        if lfp.frame:
            print "\t%-20s\t%12d" % ("metadata:", lfp.frame.metadata.size)
            print "\t%-20s\t%12d" % ("image:", lfp.frame.image.size)
            print "\t%-20s\t%12d" % ("private_metadata:", lfp.frame.private_metadata.size)
        else:
            print "\tNone"

        print
        print "Refocus-Stack:"
        if lfp.refocus_stack:
            print "\t%-20s\t%12d" % ("images:", len(lfp.refocus_stack.images))
            print "\t%-20s\t%12s" % ("depth_lut:", "%dx%d" %
                    (lfp.refocus_stack.depth_lut.width, lfp.refocus_stack.depth_lut.height))
            print "\t%-20s\t%12d" % ("default_lambda:", lfp.refocus_stack.default_lambda)
            print "\t%-20s\t%12d" % ("default_width:", lfp.refocus_stack.default_width)
            print "\t%-20s\t%12d" % ("default_height:", lfp.refocus_stack.default_height)
            print
            print "\tDepth Table:"
            for i in xrange(lfp.refocus_stack.depth_lut.width):
                print "\t\t",
                for j in xrange(lfp.refocus_stack.depth_lut.height):
                    print "%2d" % lfp.refocus_stack.depth_lut.table[j][i],
                print
        else:
            print "\tNone"

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

