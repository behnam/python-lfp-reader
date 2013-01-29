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


"""Read LFP files
"""

import os, os.path
from operator import itemgetter

import lfp_section


################################
# General

class LfpGenericError(Exception):
    """General LFP file error"""


class LfpGenericFile:
    """Generic class for any LFP file
    """

    ################
    # Internals

    def __init__(self, file_path):
        self.header = None
        self.meta = None
        self.chunks = {}
        self._file_path = file_path
        self._file_size = os.stat(file_path).st_size
        self._file = open(self._file_path, 'rb')

    def __del__(self):
        if hasattr(self, '_file') and self._file:
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
            print "Create file: %s" % exp_path
            exp_file.write(exp_data)

