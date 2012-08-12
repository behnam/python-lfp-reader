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
# Copyright (C) 2012  Behnam Esfahbod


"""Read and process an LFP Picture or LFP Storage file
"""

from __future__ import division

import sys
import os, os.path
import math
from struct import unpack
from operator import itemgetter
from collections import namedtuple

import lfp_section


################################
# General

class LfpGenericError(Exception):
    """General LFP file error"""


class LfpGenericFile:
    """Generic class for any LFP file
    """

    header = None
    meta = None
    chunks = {}

    _file_path = None
    _file_size = None
    _file = None

    ################
    # Internals

    def __init__(self, file_path):
        self._file_path = file_path
        self._file_size = os.stat(file_path).st_size
        self._file = open(self._file_path, 'rb')

    def __del__(self):
        self._file.close()

    def __repr__(self):
        return "LfpGenericFile(%s, %s, %d chunks)" % (self.header, self.meta, len(self.chunks))

    @property
    def file_path(self):
        return self._file_path

    @property
    def chunks_sorted(self):
        return sorted(self.chunks.iteritems(), key=itemgetter(0))

    ################
    # Loading

    def load(self):
        try:
            self._load_meta()
            self._load_chunks()
        except lfp_section.LfpReadError:
            raise LfpGenericError("Not a valid LFP file")

        self.process()
        return self

    def _load_meta(self):
        # Read file
        self.header = lfp_section.LfpHeader(self._file)
        self.meta = lfp_section.LfpMeta(self._file)

    def _load_chunks(self):
        while self._file.tell() <= self._file_size - lfp_section.LfpSection.MAGIC_LENGTH:
            chunk = lfp_section.LfpChunk(self._file)
            self.chunks[chunk.sha1] = chunk

    def process(self):
        """Subclasses shall implement this function"""
        pass

    ################
    # Exporting

    def export(self):
        self.export_meta()
        self.export_chunks()

    def export_meta(self):
        self.meta.export_data(self.export_path('lfp_meta', 'json'))

    def export_chunks(self):
        for sha1, chunk in self.chunks_sorted:
            chunk.export_data(self.export_path(sha1[5:], 'data'))

    def export_path(self, exp_name, exp_ext=None):
        prefix, lfp_ext = os.path.splitext(self._file_path)
        if lfp_ext != '.lfp':
            prefix = self._file_path
        if exp_ext is None:
            return "%s__%s" % (prefix, exp_name)
        else:
            return "%s__%s.%s" % (prefix, exp_name, exp_ext)

    def export_write(self, exp_name, exp_ext, exp_data):
        with open(self.export_path(exp_name, exp_ext), 'wb') as exp_file:
            exp_file.write(exp_data)


################################
# Picture file

class LfpPictureError(LfpGenericError):
    """LFP Picture file error"""


def _lfp_picture_data_class(cls_name, *args):
    """Store formatted data for LFP Picture file"""
    return namedtuple(cls_name, *args)

Frame = _lfp_picture_data_class('Frame',
        ('metadata image private_metadata'))

RefocusStack = _lfp_picture_data_class('RefocusStack',
        ('images depth_lut default_lambda default_width default_height'))

RefocusImage = _lfp_picture_data_class('RefocusImage',
        ('lambda_ width height representation chunk'))

DepthLut = _lfp_picture_data_class('DepthLut',
        ('width height representation table chunk'))


class LfpPictureFile(LfpGenericFile):
    """Load an LFP Picture file and read the data chunks on-demand
    """

    frame = None
    refocus_stack = None

    ################
    # Internals

    def __repr__(self):
        version = self.meta.content['version']
        image_size = self.frame.image.size
        return ("LfpPictureFile(version=%d.%d, image_size=%d)" %
                (version['major'], version['minor'], image_size))

    ################
    # Loading

    def process(self):
        try:
            picture_data = self.meta.content['picture']

            # Data for raw picture file
            try:
                frame_data = picture_data['frameArray'][0]['frame']
                self.frame = Frame(
                        metadata=self.chunks[frame_data['metadataRef']],
                        image=self.chunks[frame_data['imageRef']],
                        private_metadata=self.chunks[frame_data['privateMetadataRef']])

            except (KeyError, IndexError):
                pass

            # Data for refocus-stack picture file
            try:
                accel_data = picture_data['accelerationArray'][0]['vendorContent']
                default_dimensions = accel_data['displayParameters']['displayDimensions']

                images = [ RefocusImage(
                    lambda_=img['lambda'],
                    width=img['width'],
                    height=img['height'],
                    representation=img['representation'],
                    chunk=self.chunks[img['imageRef']])
                    for img in accel_data['imageArray']
                    ]

                depth_width  = accel_data['depthLut']['width']
                depth_height = accel_data['depthLut']['height']
                depth_data  = self.chunks[accel_data['depthLut']['imageRef']].data
                depth_table = [[ unpack("f",
                    depth_data[ (j*depth_width + i) * 4 : (j*depth_width + i+1) * 4 ])[0]
                    for j in xrange(depth_height)] for i in xrange(depth_width)]

                depth_lut = DepthLut(
                        width=depth_width,
                        height=depth_height,
                        representation=accel_data['depthLut']['representation'],
                        table=depth_table,
                        chunk=self.chunks[accel_data['depthLut']['imageRef']])

                self.refocus_stack = RefocusStack(
                    default_lambda=accel_data['defaultLambda'],
                    default_width=default_dimensions['value']['width'],
                    default_height=default_dimensions['value']['height'],
                    images=images,
                    depth_lut=depth_lut)

            except (KeyError, IndexError):
                pass

        except KeyError:
            raise LfpPictureError("Not a valid LFP Picture file")

    ################
    # Exporting

    def get_depth_lut_txt(self):
        depth_lut = self.refocus_stack.depth_lut
        txt = ""
        for i in xrange(depth_lut.width):
            for j in xrange(depth_lut.height):
                txt += "%9f " % depth_lut.table[j][i]
            txt += "\r\n"
        return txt

    def export(self):
        if self.frame:
            self.export_frame()
        if self.refocus_stack:
            self.export_refocus_stack()

    def export_frame(self):
        self.frame.metadata.export_data(self.export_path('frame_metadata', 'json'))
        self.frame.image.export_data(self.export_path('frame', 'raw'))
        self.frame.private_metadata.export_data(self.export_path('frame_private_metadata', 'json'))

    def export_refocus_stack(self):
        for idx, image in enumerate(self.refocus_stack.images):
            image.chunk.export_data(self.export_path('focused_%02d' % idx,
                image.representation))
        self.refocus_stack.depth_lut.chunk.export_data(self.export_path('depth_lut',
            self.refocus_stack.depth_lut.representation))
        self.export_write('depth_lut', 'txt', self.get_depth_lut_txt())

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


################################
# Storage file

class LfpStorageError(LfpGenericError):
    """LFP Storage file error"""


class LfpStorageFile(LfpGenericFile):
    """Load an LFP Storage file and read the data chunks on-demand
    """

    files = {}

    @property
    def files_sorted(self):
        return sorted(self.files.iteritems(), key=itemgetter(0))

    ################
    # Internals

    def __repr__(self):
        return "LfpStorageFile(%s, %s, %d chunks)" % (self.header, self.meta, len(self.chunks))

    ################
    # Loading

    def process(self):
        try:
            files_list = self.meta.content['files']
            self.files = dict( (f['name'], self.chunks[f['dataRef']])
                    for f in files_list )
        except KeyError:
            raise LfpStorageError("Not a valid LFP Storage file")

    ################
    # Exporting

    def export(self):
        self.export_files()

    def export_files(self):
        for path, chunk in self.files_sorted:
            chunk.export_data(self.export_path(path[3:].replace('\\', '__')))

