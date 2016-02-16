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


"""Utilities for internet usage
"""


import sys


################################
# Dict functions
def dict_items(d):
    if sys.hexversion < 0x03000000:
        return d.iteritems()
    else:
        return d.items()


################################
# Standard Library
if sys.hexversion < 0x03000000:
    from cStringIO import StringIO
    import Tkinter as tk, tkFileDialog
else:
    from io import StringIO
    import tkinter as tk
    from tkinter import filedialog as tkFileDialog


################################
# Python Imageing Library
try:
    from PIL import Image as pil
except ImportError:
    pil = None

try:
    from PIL import ImageTk as piltk
except ImportError:
    piltk = None

def check_pil_module():
    if pil is None:
        raise RuntimeError("Cannot find Python Imaging Library (PIL or Pillow)")
    if piltk is None:
        raise RuntimeError("Cannot find Tk binding for Python Imaging Library (PIL or Pillow)")


################################
# GStreamer Python
try:
    import gst_h264_splitter
except ImportError:
    gst_h264_splitter = None

def check_gst_h264_splitter_module():
    if gst_h264_splitter is None:
        raise RuntimeError("Cannot find GStreamer Python library")

