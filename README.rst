=========================================
LFP (Light Field Photography) File Reader
=========================================

<https://behnam.github.com/python-lfp-reader>

Provides a Python library and command-line scripts to read Lytro LFP files, and
a simple viewer for Lytro LFP Picture files.

Technically, there are two types of LFP files: Picture and Storage.  LFP
Storage files are used to store the data and configurations for Lytro cameras,
and LFP Picture (.lfp) files are used to store RAW and/or processed data for
Lytro light-field pictures.

This is a pure-Python package and should work on any platform.  Please report
any problems at <https://github.com/behnam/python-lfp-reader/issues>.


LFP File Format
===============

*LFP* is a new file format used in *Lytro Light Field* cameras for the RAW and
Processed picture files, as well as storing camera information in the Lytro
Desktop library.

**LFP Picture** files have a ``.lfp`` extension, and among these, the name of
the processed picture files end in ``-stk.lfp``, where *stk* stands for
refocuse "stack".  Embadding JPEG data with some additional refocus data, the
``stk.lfp`` files are designed to be used in the Lytro Desktop application and
on the web.

**LFP Storage** files embed various data files, which are identified by a
pathname, i.e. ``C:\CALIB\WIFI_MAC_ADDR.TXT``.


LFP Scripts
===========

This package provides the following command-line scripts.


Picture Viewer
--------------

**lfp_picture_viewer.py**
  A small application to view and *refocus* LFP Picture files.
  You may provide the name of the Processed LFP Picture file in the
  command-line.::
    ./lfp_picture_viewer.py samples/IMG_0001-stk.lfp

  *NOTE: This script requires Python Imaging Library (PIL) to run.*


File Information Scripts
------------------------

**lfp_file_info.py**
  Provides general information about any LFP file, including the metadata and
  the data chunks (data size and their sha1 ids).::
    ./lfp_file_info.py samples/IMG_0003.lfp
  You may also pass the sha1 id to the command line to get the content of the
  data chunk in standard output.::
    ./lfp_file_info.py samples/IMG_0001.lfp sha1-992ae2d9f755077e50de7b9b1357e873885b3382

**lfp_picture_info.py**
  Provides detailed information about a picture file.::
    ./lfp_picture_info.py samples/IMG_0003.lfp
  The *Frame* section provides the information about the RAW picture data, and
  the *RefocusStack* section provides the information about the processed image
  data, including the number of JPEG files and the size of the depth table.
  You will also get a preview of the depth table.

**lfp_storage_info.py**
  Providing a list of embedded files in an LFP Storage file.::
    ./lfp_storage_extractor.py data.C.0


Exporters
----------------

**lfp_file_exporter.py**
  Exports metadata and data sections of a generic file into separate files.::
    ./lfp_file_exporter.py samples/IMG_0001.lfp

**lfp_picture_exporter.py**
  Exports raw and processed data of a picture file into separate files.::
    ./lfp_picture_exporter.py samples/IMG_0001.lfp
    ./lfp_picture_exporter.py samples/IMG_0001-stk.lfp

**lfp_storage_exporter.py**
  Exports all the embedded files of a storage file into separate files.::
    ./lfp_storage_exporter.py data.C.0
  If you give the script a path, you get the content of that specific file
  in the standard output.::
    ./lfp_storage_exporter.py data.C.0 'C:\CALIB\WIFI_MAC_ADDR.TXT'


LFP Reader Library
=======================

**LFP Reader library (``lfp_reader``)** provides direct reading access to all
data and metadata in any LFP files. For the processed LFP Picture files, you
can easily access the JPEG data and the depth table. And for LFP Storage files,
you can access embedded files easily using their pathname.

The main classes in the ``lfp_reader`` package are:

- ``LfpGenericFile``
- ``LfpPictureFile``
- ``LfpStorageFile``


Code License
============

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


Legal Notice
============

This project is NOT affiliated with LYTRO, INC.  Lytro (R) is a trademark of
LYTRO, INC. <http://www.lytro.com/>

Some of this work is based on Nirav Patel's ``lfptools`` project and his
analysis on LFP file format.  <https://github.com/nrpatel/lfptools>

Copyright (C) 2012 Behnam Esfahbod. <http://behnam.es/>

