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
import math
from cStringIO import StringIO

import Image as PImage

from lfp_reader import LfpPictureFile


OUTPUT_FORMATS = ('jpeg', 'png')


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

        try:
            depth_lut = lfp.refocus_stack.depth_lut
            images = lfp.refocus_stack.images
            width  = lfp.refocus_stack.default_width
            height = lfp.refocus_stack.default_height
        except:
            raise Exception("Not a Processed LFP Picture file")

        p_app_focused = PImage.open(StringIO(images[0].chunk.data))
        p_images = dict((image.chunk.sha1, PImage.open(StringIO(image.chunk.data)))
            for image in images)

        for i in xrange(depth_lut.width):
            for j in xrange(depth_lut.height):
                box = (int(math.floor(width  * i / depth_lut.width)),
                       int(math.floor(height * j / depth_lut.height)),
                       int(math.floor(width  * (i+1) / depth_lut.width)),
                       int(math.floor(height * (j+1) / depth_lut.height)))
                most_focused = lfp.find_most_focused(i, j)
                p_most_focused = p_images[most_focused.chunk.sha1]
                piece = p_most_focused.crop(box)
                p_app_focused.paste(piece, box)

        for format_ in OUTPUT_FORMATS:
            output = StringIO()
            p_app_focused.save(output, format_)
            lfp.export_write('all_focus', format_, output.getvalue())
            output.close()

    except Exception as err:
        print >>sys.stderr, "Error:", err
        exit(1)

