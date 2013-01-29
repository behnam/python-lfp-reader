# python
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
# Copyright (C) 2012-2013  Behnam Esfahbod


"""Read and process LFP Picture files
"""

import sys
import math
from struct import unpack
from collections import namedtuple
from cStringIO import StringIO

try:
    import Image as PIL
except ImportError:
    PIL = None

import lfp_file

def check_pimage_module():
    if PIL is None:
        raise RuntimeError("Cannot find Python Imaging Library (PIL)")


################################
# Picture file

class LfpPictureError(lfp_file.LfpGenericError):
    """LFP Picture file error"""


def _lfp_picture_data_class(cls_name, *args):
    """Store formatted data for LFP Picture file"""
    return namedtuple(cls_name, *args)

Frame = _lfp_picture_data_class('Frame',
        'metadata image private_metadata')

RefocusStack = _lfp_picture_data_class('RefocusStack',
        'images depth_lut default_lambda default_width default_height')

RefocusImage = _lfp_picture_data_class('RefocusImage',
        'lambda_ width height representation chunk')

DepthLut = _lfp_picture_data_class('DepthLut',
        'width height representation table chunk')


class LfpPictureFile(lfp_file.LfpGenericFile):
    """Load an LFP Picture file and read the data chunks on-demand
    """

    ################
    # Internals

    def __init__(self, file_path):
        lfp_file.LfpGenericFile.__init__(self, file_path)
        self._frame = None
        self._refocus_stack = None

    def __repr__(self):
        version = self.meta.content['version']
        image_size = self._frame.image.size if self._frame else 'N/A'
        return ("LfpPictureFile(version=%s.%s, provisionalDate=%s, frame=%s)" % (
            version['major'], version['minor'],
            version['provisionalDate'],
            'True' if self._frame else 'False'
            ))

    ################
    # Loading

    def process(self):
        try:
            picture_data = self.meta.content['picture']
            frame_data = picture_data['frameArray'][0]['frame']

            # Data for raw picture file
            if (    frame_data['metadataRef']        in self.chunks and
                    frame_data['imageRef']           in self.chunks and
                    frame_data['privateMetadataRef'] in self.chunks ):
                self._frame = Frame(
                        metadata=        self.chunks[frame_data['metadataRef']],
                        image=           self.chunks[frame_data['imageRef']],
                        private_metadata=self.chunks[frame_data['privateMetadataRef']])

            # Data for processed picture file
            if picture_data['accelerationArray']:
                for accel_data in picture_data['accelerationArray']:
                    accel_type    = accel_data["type"]
                    accel_content = accel_data['vendorContent']

                    if accel_type == 'com.lytro.acceleration.refocusStack':

                        if 'imageArray' in accel_content:
                            # JPEG-based refocus stack
                            images = [
                                    RefocusImage(
                                        lambda_=img['lambda'],
                                        width=img['width'],
                                        height=img['height'],
                                        representation=img['representation'],
                                        chunk=self.chunks[img['imageRef']])
                                    for img in accel_content['imageArray'] ]

                        elif 'blockOfImages' in accel_content:
                            # H264-based refocus stack
                            #TODO process refocusStack
                            images = []

                        else:
                            raise KeyError()

                        # Depth Look-up Table
                        depth_width  = accel_content['depthLut']['width']
                        depth_height = accel_content['depthLut']['height']
                        depth_data  = self.chunks[accel_content['depthLut']['imageRef']].data
                        depth_table = [ [
                            unpack("f", depth_data[ (j*depth_width + i) * 4 : (j*depth_width + i+1) * 4 ])[0]
                            for j in xrange(depth_height) ]
                            for i in xrange(depth_width) ]

                        depth_lut = DepthLut(
                                width=depth_width,
                                height=depth_height,
                                representation=accel_content['depthLut']['representation'],
                                table=depth_table,
                                chunk=self.chunks[accel_content['depthLut']['imageRef']])

                        default_dimensions = accel_content['displayParameters']['displayDimensions']['value']
                        self._refocus_stack = RefocusStack(
                            default_lambda=accel_content['defaultLambda'],
                            default_width=default_dimensions['width'],
                            default_height=default_dimensions['height'],
                            images=images,
                            depth_lut=depth_lut)

                    elif accel_type == 'com.lytro.acceleration.edofParallax':
                        # H264-based parallax
                        #TODO process edofParallax
                        pass

                    elif accel_type == 'com.lytro.acceleration.depthMap':
                        # Depth-Map
                        #TODO process depthMap
                        pass

        except KeyError:
            #XXX
            raise
            raise LfpPictureError("Not a valid LFP Picture file")

    def get_frame(self):
        if not self._frame:
            raise LfpPictureError("%s: Not a valid Raw LFP Picture file" % self.file_path)
        return self._frame

    def get_refocus_stack(self):
        if not self._refocus_stack:
            raise LfpPictureError("%s: Not a valid Processed LFP Picture file" % self.file_path)
        if not self._refocus_stack.images:
            raise LfpPictureError("%s: LFP Picture file does not contain JPEG-based refocused stack" % self.file_path)
        return self._refocus_stack

    ################
    # Exporting

    def export(self):
        if self._frame:
            self.export_frame()
        if self._refocus_stack:
            self.export_refocus_stack()

    def export_frame(self):
        self._frame.metadata.export_data(self.get_export_path('frame_metadata', 'json'))
        self._frame.image.export_data(self.get_export_path('frame', 'raw'))
        self._frame.private_metadata.export_data(self.get_export_path('frame_private_metadata', 'json'))

    def export_refocus_stack(self):
        for idx, image in enumerate(self._refocus_stack.images):
            image.chunk.export_data(self.get_export_path('image_%02d' % idx,
                image.representation))
        self._refocus_stack.depth_lut.chunk.export_data(self.get_export_path('depth_lut',
            self._refocus_stack.depth_lut.representation))
        self.export_write('depth_lut', 'txt', self.get_depth_lut_txt())

    def export_all_focused(self, formats=('jpeg', 'png')):
        pil_all_focused = self.get_pil_all_focused()
        for format_ in formats:
            output = StringIO()
            pil_all_focused.save(output, format_)
            self.export_write('all_focused', format_, output.getvalue())
            output.close()

    def get_depth_lut_txt(self):
        depth_lut = self._refocus_stack.depth_lut
        txt = ""
        for i in xrange(depth_lut.width):
            for j in xrange(depth_lut.height):
                txt += "%9f " % depth_lut.table[j][i]
            txt += "\r\n"
        return txt

    ################
    # Printing

    def print_info(self):
        print "    Frame:"
        if self._frame:
            print "\t%-20s\t%12d" % ("metadata:", self._frame.metadata.size)
            print "\t%-20s\t%12d" % ("image:", self._frame.image.size)
            print "\t%-20s\t%12d" % ("private_metadata:", self._frame.private_metadata.size)
        else:
            print "\tNone"

        print "    Refocus-Stack:"
        if self._refocus_stack:
            print "\t%-20s\t%12d" % ("images:", len(self._refocus_stack.images))
            print "\t%-20s\t%12s" % ("depth_lut:", "%dx%d" %
                    (self._refocus_stack.depth_lut.width, self._refocus_stack.depth_lut.height))
            print "\t%-20s\t%12d" % ("default_lambda:", self._refocus_stack.default_lambda)
            print "\t%-20s\t%12d" % ("default_width:", self._refocus_stack.default_width)
            print "\t%-20s\t%12d" % ("default_height:", self._refocus_stack.default_height)
            print "\tAvailable Focus Depth:"
            print "\t\t",
            for image in self._refocus_stack.images:
                print "%5.2f" % image.lambda_,
            print
            '''TODO Depth Table is too big in new files to be shown as text
            print "\tDepth Table:"
            for i in xrange(self._refocus_stack.depth_lut.width):
                print "\t\t",
                for j in xrange(self._refocus_stack.depth_lut.height):
                    print "%5.2f" % self._refocus_stack.depth_lut.table[j][i],
            '''
        else:
            print "\tNone"

    ################
    # Processing Refocus Stack

    def find_most_focused_f(self, fx=.5, fy=.5):
        """Parameters `fx` and `fy` are floats in range [0, 1)
        """
        stk = self.get_refocus_stack()
        return self.find_most_focused(
                int(math.floor(stk.depth_lut.width  * fx)),
                int(math.floor(stk.depth_lut.height * fy)))

    def find_most_focused(self, ti, tj):
        """Parameters `ti` and `tj` are indices of the depth table
        """
        stk = self.get_refocus_stack()
        taget_lambda = stk.depth_lut.table[ti][tj]
        most_focused, min_lambda_dist = None, sys.maxint
        for image in stk.images:
            lambda_dist = math.fabs(image.lambda_ - taget_lambda)
            if lambda_dist < min_lambda_dist:
                most_focused, min_lambda_dist = image, lambda_dist
        return most_focused

    def get_pil_images(self):
        check_pimage_module()
        stk = self.get_refocus_stack()
        return dict((image.chunk.sha1, PIL.open(StringIO(image.chunk.data)))
            for image in stk.images)

    def get_pil_all_focused(self):
        check_pimage_module()
        stk = self.get_refocus_stack()
        depth_lut = stk.depth_lut
        images    = stk.images
        width     = stk.default_width
        height    = stk.default_height

        pil_all_focused = PIL.open(StringIO(images[0].chunk.data))
        pil_images = self.get_pil_images()

        for i in xrange(depth_lut.width):
            for j in xrange(depth_lut.height):
                box = (int(math.floor(width  * i / depth_lut.width)),
                       int(math.floor(height * j / depth_lut.height)),
                       int(math.floor(width  * (i+1) / depth_lut.width)),
                       int(math.floor(height * (j+1) / depth_lut.height)))
                most_focused = self.find_most_focused(i, j)
                pil_most_focused = pil_images[most_focused.chunk.sha1]
                piece = pil_most_focused.crop(box)
                pil_all_focused.paste(piece, box)
        return pil_all_focused

