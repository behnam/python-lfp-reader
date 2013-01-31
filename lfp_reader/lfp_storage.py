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


"""Read LFP Storage files
"""

from operator import itemgetter

import lfp_file


################################
# Storage file

class LfpStorageError(lfp_file.LfpGenericError):
    """LFP Storage file error"""


class LfpStorageFile(lfp_file.LfpGenericFile):
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
            chunk.export_data(self.get_export_path(path[3:].replace('\\', '__')))

