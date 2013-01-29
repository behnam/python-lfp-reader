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

import lfp_file


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
        self.frame = None
        self.refocus_stack = None

    def __repr__(self):
        version = self.meta.content['version']
        image_size = self.frame.image.size if self.frame else 'N/A'
        return ("LfpPictureFile(version=%s.%s, provisionalDate=%s, frame=%s)" % (
            version['major'], version['minor'],
            version['provisionalDate'],
            'True' if self.frame else 'False'
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
                self.frame = Frame(
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
                        self.refocus_stack = RefocusStack(
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
            raise
            raise LfpPictureError("Not a valid LFP Picture file")

    ################
    # Exporting

    def export(self):
        if self.frame:
            self.export_frame()
        if self.refocus_stack:
            self.export_refocus_stack()

    def export_frame(self):
        self.frame.metadata.export_data(self.get_export_path('frame_metadata', 'json'))
        self.frame.image.export_data(self.get_export_path('frame', 'raw'))
        self.frame.private_metadata.export_data(self.get_export_path('frame_private_metadata', 'json'))

    def export_refocus_stack(self):
        for idx, image in enumerate(self.refocus_stack.images):
            image.chunk.export_data(self.get_export_path('image_%02d' % idx,
                image.representation))
        self.refocus_stack.depth_lut.chunk.export_data(self.get_export_path('depth_lut',
            self.refocus_stack.depth_lut.representation))
        self.export_write('depth_lut', 'txt', self.get_depth_lut_txt())

    def get_depth_lut_txt(self):
        depth_lut = self.refocus_stack.depth_lut
        txt = ""
        for i in xrange(depth_lut.width):
            for j in xrange(depth_lut.height):
                txt += "%9f " % depth_lut.table[j][i]
            txt += "\r\n"
        return txt

    ################
    # Manipulation

    def find_most_focused_f(self, fx=.5, fy=.5):
        """Parameters `fx` and `fy` are floats in range [0, 1)
        """
        return self.find_most_focused(
                int(math.floor(self.refocus_stack.depth_lut.width  * fx)),
                int(math.floor(self.refocus_stack.depth_lut.height * fy)))

    def find_most_focused(self, ti, tj):
        """Parameters `ti` and `tj` are indices of the depth table
        """
        taget_lambda = self.refocus_stack.depth_lut.table[ti][tj]
        most_focused, min_lambda_dist = None, sys.maxint
        for image in self.refocus_stack.images:
            lambda_dist = math.fabs(image.lambda_ - taget_lambda)
            if lambda_dist < min_lambda_dist:
                most_focused, min_lambda_dist = image, lambda_dist
        return most_focused

