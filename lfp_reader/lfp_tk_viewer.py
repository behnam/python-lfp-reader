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


"""An LFP Picture Viewer using Tkinter GUI library
"""

from __future__ import division

import Tkinter

# Python Imageing Library
try:
    import Image as PIL, ImageTk as TkPIL
except ImportError:
    PIL = None
def _check_pil_module():
    if PIL is None:
        raise RuntimeError("Cannot find Python Imaging Library (PIL or Pillow)")


################################################################

class LfpTkViewer():
    """View and refocues Processed LFP Picture files (*-stk.lfp)
    """

    def __init__(self, lfp_picture,
            title="Light-Field Picture",
            title_pattern="%s [Python LFP Reader]",
            init_size=(648, 648)
            ):
        self._lfp = lfp_picture
        self._title = title if not title_pattern else (title_pattern % title)
        self._set_active_size(init_size)
        self._active_pil_image = None
        self._resized_tkp_image = None

        # Create tk window
        self._tkroot = Tkinter.Tk()
        self._tkroot.wm_title(self._title)
        self._tkroot.protocol("WM_DELETE_WINDOW", self.quit)
        self._tkroot.geometry("%dx%d" % self._active_size)
        self._tkroot.bind('<Configure>', self._cb_resize)

        # Create tk picture
        self._tkpic = Tkinter.Label(self._tkroot)
        self._tkpic.bind("<Button-1>", self._cb_refocus)
        self._tkpic.bind("<B1-Motion>", self._cb_refocus)
        self._tkpic.bind("<Button-2>", self._cb_all_focused)
        self._tkpic.bind("<B2-Motion>", self._cb_all_focused)
        self._tkpic.bind("<Button-3>", self._cb_parallax)
        self._tkpic.bind("<B3-Motion>", self._cb_parallax)
        self._tkpic.pack()

        # Verify and init view
        if True:
            #todo support non-refocus-based LFP pictures
            self._lfp.get_refocus_stack()
            self.do_refocus_at(.5, .5)

        self._tkroot.mainloop()

    def quit(self):
        self._tkroot.destroy()
        self._tkroot.quit()


    ################################
    # Display Image

    def _cb_resize(self, event):
        self._set_active_size((event.width, event.height))
        self._redraw_active_image()

    def _set_active_size(self, size):
        self._active_size = (min(size[0], size[1]), )*2
        self._resized_pil_cache = {}

    def show_image_by_group_id(self, group, image_id):
        pil_image = self._lfp.get_pil_image(group, image_id)
        return self.show_pil_image(pil_image)

    def show_pil_image(self, pil_image):
        if pil_image == self._active_pil_image: return False
        self._active_pil_image  = pil_image
        self._redraw_active_image()
        return True

    def _redraw_active_image(self):
        self._resized_pil_image = self._get_resized_pil_image(self._active_pil_image)
        '''
        if not hasattr(self, '_resized_tkp_image'):
            self._resized_tkp_image = TkPIL.PhotoImage(self._resized_pil_image)
        else:
            self._resized_tkp_image.paste(self._resized_pil_image)
        '''
        self._resized_tkp_image = TkPIL.PhotoImage(self._resized_pil_image)
        self._tkpic.configure(image=self._resized_tkp_image)

    def _get_resized_pil_image(self, pil_image):
        if pil_image not in self._resized_pil_cache:
            self._resized_pil_cache[pil_image] = pil_image.resize(self._active_size, PIL.ANTIALIAS)
        return self._resized_pil_cache[pil_image]


    ################################
    # Refocus

    def do_refocus_at(self, x_f, y_f):
        try:
            closest_refocus = self._lfp.find_closest_refocus_image(x_f, y_f)
        except:
            return False
        return self.show_image_by_group_id('refocus', closest_refocus.id)

    def _cb_refocus(self, event):
        coords_f = [event.x / self._active_size[0],
                    event.y / self._active_size[1]]
        self.do_refocus_at(*coords_f)


    ################################
    # All-Focused

    def do_all_focused(self):
        return self.show_image_by_group_id('all_focused', None)

    def _cb_all_focused(self, event):
        self.do_all_focused()


    ################################
    # Parallax

    def do_parallax_at(self, x_f, y_f):
        try:
            closest_parallax = self._lfp.find_closest_parallax_image(x_f, y_f)
        except:
            return False
        return self.show_image_by_group_id('parallax', closest_parallax.id)

    def _cb_parallax(self, event):
        self.do_parallax_at(
                event.x / self._active_size[0],
                event.y / self._active_size[1])

