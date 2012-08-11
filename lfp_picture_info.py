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


"""Show information about LFP (Light Field Photography) Picture file
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

