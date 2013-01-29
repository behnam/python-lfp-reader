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


"""Show information about LFP Picture file
"""


import os.path
import sys

from lfp_reader import LfpPictureFile

def print_lfp_picture_info(lfp_path):
    print lfp_path

    lfp = LfpPictureFile(lfp_path).load()

    print "    Frame:"
    if lfp.frame:
        print "\t%-20s\t%12d" % ("metadata:", lfp.frame.metadata.size)
        print "\t%-20s\t%12d" % ("image:", lfp.frame.image.size)
        print "\t%-20s\t%12d" % ("private_metadata:", lfp.frame.private_metadata.size)
    else:
        print "\tNone"

    print "    Refocus-Stack:"
    if lfp.refocus_stack:
        print "\t%-20s\t%12d" % ("images:", len(lfp.refocus_stack.images))
        print "\t%-20s\t%12s" % ("depth_lut:", "%dx%d" %
                (lfp.refocus_stack.depth_lut.width, lfp.refocus_stack.depth_lut.height))
        print "\t%-20s\t%12d" % ("default_lambda:", lfp.refocus_stack.default_lambda)
        print "\t%-20s\t%12d" % ("default_width:", lfp.refocus_stack.default_width)
        print "\t%-20s\t%12d" % ("default_height:", lfp.refocus_stack.default_height)
        print "\tAvailable Focus Depth:"
        print "\t\t",
        for image in lfp.refocus_stack.images:
            print "%5.2f" % image.lambda_,
        '''TODO Depth Table is too big in new files to be shown as text
        print "\tDepth Table:"
        for i in xrange(lfp.refocus_stack.depth_lut.width):
            print "\t\t",
            for j in xrange(lfp.refocus_stack.depth_lut.height):
                print "%5.2f" % lfp.refocus_stack.depth_lut.table[j][i],
        '''
    else:
        print "\tNone"


def main(lfp_paths):
    first = True
    for lfp_path in lfp_paths:
        if not first: print
        first = False
        print_lfp_picture_info(lfp_path)


def usage(errcode=0, of=sys.stderr):
    print >>of, ("Usage: %s picture.lfp [picture-2.lfp ...]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)


if __name__=='__main__':
    if len(sys.argv) < 2:
        usage(1)
    try:
        main(sys.argv[1:])
    except Exception as err:
        print >>sys.stderr, "Error:", err
        if sys.platform == 'win32': raw_input()
        exit(1)

