# python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://code.behnam.es/python-lfp-reader/
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


from __future__ import division, print_function

import sys
import math
from struct import unpack
from collections import namedtuple

from . import lfp_file
from ._utils import (
        StringIO, dict_items,
        pil, check_pil_module,
        gst_h264_splitter, check_gst_h264_splitter_module )


################################################################
# Picture file

class LfpPictureError(lfp_file.LfpGenericError):
    """LFP Picture file error"""


def _lfp_picture_data_class(cls_name, *args):
    """Store formatted data for LFP Picture file"""
    return namedtuple(cls_name, *args)

Frame = _lfp_picture_data_class('Frame',
        'metadata image private_metadata')

RefocusStack = _lfp_picture_data_class('RefocusStack',
        'refocus_images depth_lut default_lambda min_lambda max_lambda width height')

RefocusImage = _lfp_picture_data_class('RefocusImage',
        'id lambda_ width height representation chunk data')

ParallaxStack = _lfp_picture_data_class('ParallaxStack',
        'parallax_images width height viewpoint_width viewpoint_height')

ParallaxImage = _lfp_picture_data_class('ParallaxImage',
        'id coord width height representation chunk data')

DepthLut = _lfp_picture_data_class('DepthLut',
        'width height representation table chunk')

Coord = _lfp_picture_data_class('Coord',
        'x y')


class LfpPictureFile(lfp_file.LfpGenericFile):
    """Load an LFP Picture file and read the data chunks on-demand
    """

    ################################
    # Internals

    def __init__(self, file_):
        lfp_file.LfpGenericFile.__init__(self, file_)
        self._frame = None
        self._refocus_stack = None
        self._parallax_stack = None
        self._pil_cache = {}

    def __repr__(self):
        version = self.meta.content['version']
        image_size = self._frame.image.size if self._frame else 'N/A'
        return ("LfpPictureFile(version=%s.%s, provisionalDate=%s, frame=%s)" % (
            version['major'], version['minor'],
            version['provisionalDate'],
            'True' if self._frame else 'False'
            ))

    ################################
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
                    accel_type    = accel_data['type']
                    accel_content = accel_data['vendorContent']

                    if accel_type == 'com.lytro.acceleration.refocusStack':
                        # Refocuse Stack
                        refocus_images = {}

                        if 'imageArray' in accel_content:
                            # JPEG-based refocus stack
                            for id, rimg in enumerate(accel_content['imageArray']):
                                refocus_images[id] = RefocusImage(
                                        id=id,
                                        lambda_=rimg['lambda'],
                                        width=rimg['width'],
                                        height=rimg['height'],
                                        representation=rimg['representation'],
                                        chunk=self.chunks[rimg['imageRef']],
                                        data=None)

                        elif 'blockOfImages' in accel_content:
                            block_of_images = accel_content['blockOfImages']
                            if block_of_images['representation'] == 'h264':
                                # H264-encoded refocus stack
                                check_gst_h264_splitter_module()
                                images_representation = 'jpeg'
                                h264_data = self.chunks[block_of_images['blockOfImagesRef']].data
                                h264_splitter = gst_h264_splitter.H246Splitter(h264_data, image_format=images_representation)
                                images_data = h264_splitter.get_images()
                                for id, rimg in enumerate(block_of_images['metadataArray']):
                                    refocus_images[id] = RefocusImage(
                                            id=id,
                                            lambda_=rimg['lambda'],
                                            width=rimg['width'],
                                            height=rimg['height'],
                                            representation=images_representation,
                                            chunk=None,
                                            data=images_data[id])

                            else:
                                raise KeyError('Unsupported Processed LFP Picture file')

                        else:
                            raise KeyError('Unsupported Processed LFP Picture file')

                        # Depth Look-up Table
                        depth_width  = accel_content['depthLut']['width']
                        depth_height = accel_content['depthLut']['height']
                        depth_data  = self.chunks[accel_content['depthLut']['imageRef']].data
                        depth_table = [ [
                            unpack("f", depth_data[ (j*depth_width + i) * 4 : (j*depth_width + i+1) * 4 ])[0]
                            for j in range(depth_height) ]
                            for i in range(depth_width) ]

                        depth_lut = DepthLut(
                                width=depth_width,
                                height=depth_height,
                                representation=accel_content['depthLut']['representation'],
                                table=depth_table,
                                chunk=self.chunks[accel_content['depthLut']['imageRef']])

                        default_dimensions = accel_content['displayParameters']['displayDimensions']['value']
                        min_lambda_i = min(refocus_images, key=lambda id: refocus_images[id].lambda_)
                        max_lambda_i = max(refocus_images, key=lambda id: refocus_images[id].lambda_)
                        self._refocus_stack = RefocusStack(
                            default_lambda=accel_content['defaultLambda'],
                            min_lambda=refocus_images[min_lambda_i].lambda_,
                            max_lambda=refocus_images[max_lambda_i].lambda_,
                            width=default_dimensions['width'],
                            height=default_dimensions['height'],
                            refocus_images=refocus_images,
                            depth_lut=depth_lut)

                    elif accel_type == 'com.lytro.acceleration.edofParallax':
                        # Extended Depth-Of-Field/Parallax
                        block_of_images = accel_content['blockOfImages']
                        parallax_images = { }

                        if block_of_images['representation'] == 'h264':
                            # H264-encoded parallax stack
                            check_gst_h264_splitter_module()
                            images_representation = 'jpeg'
                            h264_data = self.chunks[block_of_images['blockOfImagesRef']].data
                            h264_splitter = gst_h264_splitter.H246Splitter(h264_data, image_format=images_representation)
                            images_data = h264_splitter.get_images()
                            for id, pimg in enumerate(block_of_images['metadataArray']):
                                parallax_images[id] = ParallaxImage(
                                    id=id,
                                    coord=Coord(**pimg['coord']),
                                    width=pimg['width'],
                                    height=pimg['height'],
                                    representation=images_representation,
                                    chunk=None,
                                    data=images_data[id])

                        max_coord_x_i = max(parallax_images, key=lambda id: parallax_images[id].coord.x)
                        max_coord_y_i = max(parallax_images, key=lambda id: parallax_images[id].coord.y)
                        default_dimensions = accel_content['displayParameters']['displayDimensions']['value']
                        self._parallax_stack = ParallaxStack(
                            width    = default_dimensions['width'],
                            height   = default_dimensions['height'],
                            parallax_images  = parallax_images,
                            viewpoint_width  = 2 * parallax_images[max_coord_x_i].coord.x,
                            viewpoint_height = 2 * parallax_images[max_coord_y_i].coord.y)

                    elif accel_type == 'com.lytro.acceleration.depthMap':
                        # Depth-Map
                        #todo process depthMap
                        pass

        except KeyError:
            raise LfpPictureError("Not a valid/supported LFP Picture file")

    def has_frame(self):
        return self._frame is not None
    def get_frame(self):
        if not self.has_frame():
            raise LfpPictureError("%s: Not a valid/supported Raw LFP Picture file" % self.file_path)
        return self._frame

    def has_refocus_stack(self):
        return self._refocus_stack is not None and self._refocus_stack.refocus_images
    def get_refocus_stack(self):
        if not self.has_refocus_stack():
            raise LfpPictureError("%s: Cannot find refocus data in LFP Picture file" % self.file_path)
        return self._refocus_stack

    def has_parallax_stack(self):
        return self._parallax_stack is not None and self._parallax_stack.parallax_images
    def get_parallax_stack(self):
        if not self.has_parallax_stack():
            raise LfpPictureError("%s: Cannot find parallax data in LFP Picture file" % self.file_path)
        return self._parallax_stack


    ################################
    # Exporting

    def export(self):
        if self._frame:
            self.export_frame()
        if self._refocus_stack:
            self.export_refocus_stack()
            self.export_all_focused()
        if self._parallax_stack:
            self.export_parallax_stack()

    def export_frame(self):
        self._frame.metadata.export_data(self.get_export_path('frame_metadata', 'json'))
        self._frame.image.export_data(self.get_export_path('frame', 'raw'))
        self._frame.private_metadata.export_data(self.get_export_path('frame_private_metadata', 'json'))

    def export_refocus_stack(self):
        for id, rimg in dict_items(self._refocus_stack.refocus_images):
            r_image_name = 'refocus_%02d' % id
            if rimg.chunk:
                rimg.chunk.export_data(self.get_export_path(r_image_name, rimg.representation))
            else:
                self.export_write(r_image_name, rimg.representation, rimg.data)

        self._refocus_stack.depth_lut.chunk.export_data(self.get_export_path('depth_lut',
            self._refocus_stack.depth_lut.representation))
        self.export_write('depth_lut', 'txt', self.get_depth_lut_txt())

    def export_parallax_stack(self):
        for id, pimg in dict_items(self._parallax_stack.parallax_images):
            r_image_name = 'parallax_%02d' % id
            if pimg.chunk:
                pimg.chunk.export_data(self.get_export_path(r_image_name, pimg.representation))
            else:
                self.export_write(r_image_name, pimg.representation, pimg.data)

    def export_all_focused(self, export_format='jpeg'):
        pil_all_focused_image = self.get_pil_image('all_focused')
        output = StringIO()
        pil_all_focused_image.save(output, export_format)
        self.export_write('all_focused', export_format, output.getvalue())
        output.close()

    def get_depth_lut_txt(self):
        depth_lut = self._refocus_stack.depth_lut
        txt = ""
        for i in range(depth_lut.width):
            for j in range(depth_lut.height):
                txt += "%9f " % depth_lut.table[j][i]
            txt += "\r\n"
        return txt


    ################################
    # Printing

    def print_info(self, file=sys.stdout):
        if self._frame:
            file.writelines([
                "    Frame:\n",
                "\t%-20s\t%12d\n" % ("metadata:", self._frame.metadata.size),
                "\t%-20s\t%12d\n" % ("image:", self._frame.image.size),
                "\t%-20s\t%12d\n" % ("private_metadata:", self._frame.private_metadata.size),
                ])
        else:
            file.write("    Frame:           N/A\n")

        if self._refocus_stack:
            rstk = self.get_refocus_stack()
            file.writelines([
                "    Refocus-Stack:\n",
                "\t%-20s\t%12d\n"   % ("refocus_images#:", len(rstk.refocus_images)),
                "\t%-20s\t%12s\n"   % ("depth_lut:", "%dx%d" % (rstk.depth_lut.width, rstk.depth_lut.height)),
                "\t%-20s\t%12.2f\n" % ("default_lambda:", rstk.default_lambda),
                "\t%-20s\t%12.2f\n" % ("minimum_lambda:", rstk.min_lambda),
                "\t%-20s\t%12.2f\n" % ("maximum_lambda:", rstk.max_lambda),
                "\t%-20s\t%12d\n"   % ("default_width:", rstk.width),
                "\t%-20s\t%12d\n"   % ("default_height:", rstk.height),
                ])
            file.writelines([
                "\tlambdas:\n",
                "\t    [ "])
            file.writelines("%5.2f " % rimg.lambda_
                    for id, rimg in dict_items(rstk.refocus_images))
            file.write("]\n")
        else:
            file.write("    Refocus-Stack:   N/A\n")

        if self._parallax_stack:
            pstk = self.get_parallax_stack()
            file.writelines([
                "    Parallax-Stack:\n",
                "\t%-20s\t%12d\n"   % ("parallax_images#:", len(pstk.parallax_images)),
                "\t%-20s\t%12.2f\n" % ("viewpoint_width:", pstk.viewpoint_width),
                "\t%-20s\t%12.2f\n" % ("viewpoint_height:", pstk.viewpoint_height),
                "\t%-20s\t%12d\n"   % ("default_width:", pstk.width),
                "\t%-20s\t%12d\n"   % ("default_height:", pstk.height),
                ])
            file.writelines([
                "\tcoordinates:\n",
                "\t    [ "])
            file.writelines("(%.2f, %.2f) " % pimg.coord
                for id, pimg in dict_items(pstk.parallax_images))
            file.write("]\n")
        else:
            file.write("    Parallax-Stack:   N/A\n")

    ################################
    # Processing, Common

    def get_pil_image(self, group, image_id=None):
        """Cache and return a pil.Image instances

        Parameter `group' shall be one of ('refocus', 'parallax', 'all_focused')
        """
        check_pil_module()
        if group not in ('refocus', 'parallax', 'all_focused'):
            raise KeyError('Unknown pil cache group: %s' % group)
        cache = self._pil_cache
        if group not in cache:
            cache[group] = {}

        if group == 'all_focused' and image_id is None:
            image_id = '_'
            if image_id not in cache[group]:
                cache[group][image_id] = self._gen_pil_all_focused_image()
            return cache[group][image_id]

        if group == 'refocus' and image_id is not None:
            img = self.get_refocus_stack().refocus_images[image_id]
        elif group == 'parallax' and image_id is not None:
            img = self.get_parallax_stack().parallax_images[image_id]
        else:
            raise KeyError('Invalid image_id: %s' % image_id)

        if image_id not in cache[group]:
            data = img.data if img.data else img.chunk.data
            cache[group][image_id] = pil.open(StringIO(data))
        return cache[group][image_id]

    def preload_pil_images(self):
        if self.has_refocus_stack():
            for id in self.get_refocus_stack().refocus_images:
                self.get_pil_image('refocus', id)
            self.get_pil_image('all_focused')
        if self.has_parallax_stack():
            for id in self.get_parallax_stack().parallax_images:
                self.get_pil_image('parallax', id)


    ################################
    # Processing Refocus Stack

    def find_closest_refocus_image(self, x_f=.5, y_f=.5):
        """Parameters `x_f' and `y_f' are floats in range [0, 1)
        """
        rstk = self.get_refocus_stack()
        return self.find_closest_refocus_image_by_lut_idx(
                x_f * rstk.depth_lut.width,
                y_f * rstk.depth_lut.height)

    def find_closest_refocus_image_by_lut_idx(self, ti, tj):
        """Parameters `ti' and `tj' are indices of the depth look-up table
        """
        rstk = self.get_refocus_stack()
        ti = max(0, min(int(math.floor(ti)), rstk.depth_lut.width-1))
        tj = max(0, min(int(math.floor(tj)), rstk.depth_lut.height-1))
        lambda_ = rstk.depth_lut.table[ti][tj]
        return self._find_closest_refocus_image_by_lambda(lambda_)

    def find_closest_refocus_image_by_lambda(self, lambda_):
        rstk = self.get_refocus_stack()
        return self._find_closest_refocus_image_by_lambda(lambda_)

    def _find_closest_refocus_image_by_lambda(self, lambda_):
        rstk = self.get_refocus_stack()
        closest_image_id = min(rstk.refocus_images,
                key=lambda id: math.fabs(rstk.refocus_images[id].lambda_ - lambda_))
        return rstk.refocus_images[closest_image_id]

    def _gen_pil_all_focused_image(self):
        """Return pil.Image instance collaged from refocus images
        """
        check_pil_module()
        rstk = self.get_refocus_stack()
        depth_lut = rstk.depth_lut
        r_images  = rstk.refocus_images
        width     = rstk.width
        height    = rstk.height

        init_data = r_images[0].data if r_images[0].data else r_images[0].chunk.data
        pil_all_focused_image = pil.open(StringIO(init_data))

        for i in range(depth_lut.width):
            for j in range(depth_lut.height):
                box = (int(math.floor(width  * i / depth_lut.width)),
                       int(math.floor(height * j / depth_lut.height)),
                       int(math.floor(width  * (i+1) / depth_lut.width)),
                       int(math.floor(height * (j+1) / depth_lut.height)))
                closest_image = self.find_closest_refocus_image_by_lut_idx(i, j)
                pil_all_focused = self.get_pil_image('refocus', closest_image.id)
                piece = pil_all_focused.crop(box)
                pil_all_focused_image.paste(piece, box)
        return pil_all_focused_image

    def get_default_lambda(self):
        return self.get_refocus_stack().default_lambda
    def get_min_lambda(self):
        return self.get_refocus_stack().min_lambda
    def get_max_lambda(self):
        return self.get_refocus_stack().max_lambda


    ################################
    # Processing Parallax Stack

    def find_closest_parallax_image(self, x_f=.5, y_f=.5):
        """Parameters `x_f' and `y_f' are floats in range [0, 1)
        """
        pstk = self.get_parallax_stack()
        x_f = max(0, min(x_f, 1))
        y_f = max(0, min(y_f, 1))
        viewpoint_coord = Coord((x_f-.5) * pstk.viewpoint_width,
                                (y_f-.5) * pstk.viewpoint_height)
        closest_image, min_euclidean_dist = None, sys.maxint
        for id, pimg in dict_items(pstk.parallax_images):
            euclidean_dist = ( (pimg.coord.x-viewpoint_coord.x)**2
                             + (pimg.coord.y-viewpoint_coord.y)**2 )
            if euclidean_dist < min_euclidean_dist:
                closest_image, min_euclidean_dist = pimg, euclidean_dist
        return closest_image

