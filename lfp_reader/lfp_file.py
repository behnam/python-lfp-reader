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


"""Read LFP files
"""


from __future__ import division, print_function

import sys
import os, os.path
import json
from operator import itemgetter

from .lfp_logging import log
from . import lfp_section
from ._utils import dict_items


################################################################
# General

class LfpGenericError(Exception):
    """General LFP file error"""


class LfpGenericFile:
    """Generic class for any LFP file
    """

    ################################
    # Internals

    def __init__(self, file_):
        self.header = None
        self.meta = None
        self.chunks = {}
        self._is_loaded = False
        if isinstance(file_, (str)):
            self._file_path = file_
            self._file = open(self._file_path, 'rb')
        else:
            self._file = file_
            self._file_path = file_.name
        self._file_size = os.stat(self._file_path).st_size

    def __del__(self):
        if hasattr(self, '_file') and self._file:
            self._file.close()

    def __repr__(self):
        return "LfpGenericFile(%s, %s, %d chunks)" % (self.header, self.meta, len(self.chunks))

    @property
    def file_path(self):
        return self._file_path

    @property
    def file_name(self):
        return os.path.basename(self._file_path)

    @property
    def chunks_sorted(self):
        return sorted(dict_items(self.chunks), key=itemgetter(0))

    ################################
    # Loading

    def load(self):
        if self._is_loaded:
            return
        try:
            self._load_meta()
            self._load_chunks()
        except lfp_section.LfpReadError:
            raise LfpGenericError("Not a valid LFP file")

        self.process()

        self._is_loaded = True
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

    ################################
    # Exporting

    def export(self):
        self.export_meta()
        self.export_chunks()

    def export_meta(self):
        self.meta.export_data(self.get_export_path('lfp_meta', 'json'))

    def export_chunks(self):
        for sha1, chunk in self.chunks_sorted:
            chunk.export_data(self.get_export_path(sha1[5:], 'data'))

    def get_export_path(self, exp_name, exp_ext=None):
        prefix, lfp_ext = os.path.splitext(self._file_path)
        if lfp_ext != '.lfp':
            prefix = self._file_path
        if exp_ext is None:
            return "%s__%s" % (prefix, exp_name)
        else:
            return "%s__%s.%s" % (prefix, exp_name, exp_ext)

    def export_write(self, exp_name, exp_ext, exp_data):
        exp_path = self.get_export_path(exp_name, exp_ext)
        with open(exp_path, 'wb') as exp_file:
            log("Create file: %s" % exp_path)
            exp_file.write(exp_data)


    ################################
    # Printing

    def print_info(self, file=sys.stdout):
        """Write file metadata and list its data chunks
        """
        file.write("    Metadata:\n")
        file.writelines("\t%s\n" % line
                for line in json.dumps(self.meta.content, indent=4).split('\n'))
        file.write("\n")
        file.write("    Data Chunks: %d\n" % len(self.chunks))
        file.writelines("\t%s : %d B\n" % (sha1, chunk.size)
                for sha1, chunk in self.chunks_sorted)

