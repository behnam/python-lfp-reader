# python

# todo license
# todo copyright


"""todo
"""

import os
from collections import namedtuple
import struct

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
    _inf = None

    ################
    # Internals

    def __init__(self, file_path):
        self._file_path = file_path
        self._file_size = os.stat(file_path).st_size
        self.open_file()

    def __del__(self):
        if self._inf is not None and not self._inf.closed:
            self.close_file()

    def __repr__(self):
        return "LfpGenericFile(%s, %s, %d chunks)" % (self.header, self.meta, len(self.chunks))

    @property
    def file_path(self): return self._file_path

    ################
    # File handling

    def open_file(self):
        self._inf = open(self._file_path, 'rb')

    def close_file(self):
        self._inf.close()

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
        self.header = lfp_section.LfpHeader(self._inf)
        self.meta = lfp_section.LfpMeta(self._inf)

    def _load_chunks(self):
        while self._inf.tell() <= self._file_size - lfp_section.LfpSection.MAGIC_LENGTH:
            chunk = lfp_section.LfpChunk(self._inf)
            self.chunks[chunk.sha1] = chunk

    def process(self):
        """Subclasses shall implement this function"""
        pass


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
        ('width height representation table'))


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
    # Processing

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
                depth_table = [[ struct.unpack("f",
                    depth_data[ (j*depth_width + i) * 4 : (j*depth_width + i+1) * 4 ])[0]
                    for j in xrange(depth_height)] for i in xrange(depth_width)]

                depth_lut = DepthLut(
                        width=depth_width,
                        height=depth_height,
                        representation=accel_data['depthLut']['representation'],
                        table=depth_table)

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


################################
# Storage file

class LfpStorageError(LfpGenericError):
    """LFP Storage file error"""


class LfpStorageFile(LfpGenericFile):
    """Load an LFP Storage file and read the data chunks on-demand
    """

    ################
    # Internals

    def __repr__(self):
        return "LfpStorageFile(%s, %s, %d chunks)" % (self.header, self.meta, len(self.chunks))

    ################
    # Processing

    def process(self):
        try:
            files_list = self.meta.content['files']
            self.files = dict( (fj['name'], self.chunks[fj['dataRef']])
                    for fj in files_list )
        except KeyError:
            raise LfpStorageError("Not a valid LFP Storage file")

