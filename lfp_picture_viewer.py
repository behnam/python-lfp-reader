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
# Copyright (C) 2012-2013  Behnam Esfahbod


"""View and refocus LFP Picture file
"""


from __future__ import division

import os.path
import sys
from cStringIO import StringIO

import Tkinter
import tkFileDialog

try:
    import Image, ImageTk
except ImportError:
    pass

from lfp_reader import LfpPictureFile, LfpPictureError


class LfpPictureViewer():
    """View and refocues Processed LFP Picture files (*-stk.lfp)
    """

    def __init__(self, lfp_path=None, size=(648, 648)):
        self._active_size = size

        self._tkroot = Tkinter.Tk()
        self._lfp_path = lfp_path
        if lfp_path is None:
            self._lfp_path = tkFileDialog.askopenfilename(defaultextension="lfp")
        self._tkroot.wm_title(os.path.basename(self._lfp_path))
        self._tkroot.protocol("WM_DELETE_WINDOW", self.quit)
        self._tkroot.geometry("%dx%d" % self._active_size)
        #self._tkroot.bind('<Configure>', self.resize)

        self._lfp = LfpPictureFile(self._lfp_path).load()
        self._depth_lut = self._lfp.get_refocus_stack().depth_lut
        self._pil_images = self._lfp.get_pil_images()

        self._pic = Tkinter.Label(self._tkroot)
        self._pic.bind("<Button-1>", self.click)
        self._pic.pack()

        self.focus_image()

        self._tkroot.mainloop()

    def focus_image(self, x=.5, y=.5):
        self._active_sha1 = self._lfp.find_most_focused_f(x, y).chunk.sha1
        self.draw_image(self._active_size)

    def draw_image(self, size):
        #self._active_image = self._pil_images[self._active_sha1].resize(size, Image.ANTIALIAS)
        self._active_image = self._pil_images[self._active_sha1].resize(size, Image.ANTIALIAS)
        self._pimage = ImageTk.PhotoImage(self._active_image)
        self._pic.configure(image=self._pimage)

    def click(self, event):
        self.focus_image(event.x / self._active_size[0],
                         event.y / self._active_size[1])

    def quit(self):
        self._tkroot.destroy()
        self._tkroot.quit()


def main(lfp_paths):
    if len(lfp_paths) > 0:
        for idx, lfp_path in enumerate(lfp_paths):
            if idx > 0: print
            print "LFP Picture file: %s" % lfp_path
            LfpPictureViewer(lfp_path)
    else:
        LfpPictureViewer()


def usage(errcode=0, of=sys.stderr):
    print >>of, ("Usage: %s picture-stk.lfp [picture-stk-2.lfp ...]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)


if __name__=='__main__':
    if len(sys.argv) < 1:
        usage(1)
    try:
        main(sys.argv[1:])
    except Exception as err:
        print >>sys.stderr, "Error:", err
        if sys.platform == 'win32': raw_input()
        exit(1)

