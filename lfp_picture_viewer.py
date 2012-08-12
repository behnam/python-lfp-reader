#!/usr/bin/env python
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


"""View and refocus LFP Picture file
"""


from __future__ import division

import os.path
import sys
from cStringIO import StringIO

import Tkinter
import tkFileDialog

import Image, ImageTk

from lfp_reader import LfpPictureFile


class LfpPictureViewer():
    """View and refocues Processed LFP Picture files (*-stk.lfp)
    """

    _active_size = (648, 648)
    _tkroot = None
    _lfp_path = None
    _lfp = None
    _active_sha1 = None
    _images = None
    _depth_lut = None

    def __init__(self, lfp_path=None):
        self._tkroot = Tkinter.Tk()
        self._lfp_path = lfp_path
        if lfp_path is None:
            self._lfp_path = tkFileDialog.askopenfilename(defaultextension="lfp")
        self._tkroot.wm_title(os.path.basename(self._lfp_path))
        self._tkroot.protocol("WM_DELETE_WINDOW", self.quit)
        self._tkroot.geometry("%dx%d" % self._active_size)
        #self._tkroot.bind('<Configure>', self.resize)

        self._lfp = LfpPictureFile(self._lfp_path).load()
        try:
            self._depth_lut = self._lfp.refocus_stack.depth_lut
            self._images = dict( (i.chunk.sha1, Image.open(StringIO(i.chunk.data)))
                for i in self._lfp.refocus_stack.images)
        except:
            raise Exception("Not a Processed LFP Picture file")

        self._pic = Tkinter.Label(self._tkroot)
        self._pic.bind("<Button-1>", self.click)
        self._pic.pack()

        self.focus_image()

        self._tkroot.mainloop()

    def focus_image(self, x=.5, y=.5):
        self._active_sha1 = self._lfp.find_most_focused_f(x, y).chunk.sha1
        self.draw_image(self._active_size)

    def draw_image(self, size):
        self._active_image = self._images[self._active_sha1].resize(size, Image.ANTIALIAS)
        self._pimage = ImageTk.PhotoImage(self._active_image)
        self._pic.configure(image=self._pimage)

    def click(self, event):
        self.focus_image(event.x / self._active_size[0],
                         event.y / self._active_size[1])

    def quit(self):
        self._tkroot.destroy()
        self._tkroot.quit()


def usage(errcode=0, of=sys.stderr):
    print >>of, ("Usage: %s picture-stk.lfp" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)


def main(args):
    if len(args) < 1 or len(args) > 2:
        usage(1)
    lfp_path = args[1] if len(args) > 1 else None

    LfpPictureViewer(lfp_path)

if __name__=='__main__':
    try:
        main(sys.argv)
    except Exception as err:
        print >>sys.stderr, "Error:", err
        if sys.platform == 'win32':
            raw_input()
        exit(1)

