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
import sys
import os.path

import Tkinter, tkFileDialog

# Python Imageing Library
try:
    import Image as PIL, ImageTk as TkPIL
except ImportError:
    PIL = None
def _check_pil_module():
    if PIL is None:
        raise RuntimeError("Cannot find Python Imaging Library (PIL or Pillow)")

from lfp_reader import LfpPictureFile


################################################################

class LfpTkViewer():
    """View and refocues Processed LFP Picture files
    """

    def __init__(self,
            lfp_paths=None,
            title_pattern="{file_path}   ({index}/{count})   Python LFP Reader",
            init_size=(648, 648)):
        self._title_pattern = title_pattern
        self._lfp_picture_cache = {}
        self._lfp = None
        self._active_size = None
        self._active_pil_image = None
        self._active_refocus_lambda = 0
        self._active_parallax_viewp = (.5, .5)

        # Create tk window
        self._tk_root = Tkinter.Tk()
        self._tk_root.protocol("WM_DELETE_WINDOW", self.quit)
        self._tk_root.geometry("%dx%d" % init_size)
        self._tk_root.configure(background='black')
        self._tk_root.wm_title("Python LFP Reader")
        # window
        self._tk_root.bind_all('<Configure>',   self._cb_resize)
        self._tk_root.bind_all('<Control-w>',   self.quit)
        self._tk_root.bind_all('<Control-q>',   self.quit_force)
        # navigation: next
        self._tk_root.bind_all("<Right>",       self.next_lfp)
        self._tk_root.bind_all("<n>",           self.next_lfp)
        self._tk_root.bind_all("<space>",       self.next_lfp)
        # navigation: previous
        self._tk_root.bind_all("<Left>",        self.prev_lfp)
        self._tk_root.bind_all("<p>",           self.prev_lfp)
        self._tk_root.bind_all("<BackSpace>",   self.prev_lfp)

        # Create tk picture
        self._tk_pic = Tkinter.Label(self._tk_root)
        self._tk_pic.pack()
        # image: refocuse by click
        self._tk_pic.bind_all("<Button-1>",     self._cb_refocus_at)
        self._tk_pic.bind_all("<B1-Motion>",    self._cb_refocus_at)
        # image: refocuse by lambda
        self._tk_pic.bind_all("<Up>",           self._cb_refocus_farther)
        self._tk_pic.bind_all("<Button-4>",     self._cb_refocus_farther)
        self._tk_pic.bind_all("<Down>",         self._cb_refocus_closer)
        self._tk_pic.bind_all("<Button-5>",     self._cb_refocus_closer)
        # image: all focused
        self._tk_pic.bind_all("<Button-2>",     self._cb_all_focused)
        self._tk_pic.bind_all("<Escape>",       self._cb_all_focused)
        # image: parallax
        self._tk_pic.bind_all("<Button-3>",     self._cb_parallax_at)
        self._tk_pic.bind_all("<B3-Motion>",    self._cb_parallax_at)
        self._tk_pic.bind_all("<a>",            self._cb_parallax_left)
        self._tk_pic.bind_all("<d>",            self._cb_parallax_right)
        self._tk_pic.bind_all("<w>",            self._cb_parallax_up)
        self._tk_pic.bind_all("<s>",            self._cb_parallax_down)
        # image: save
        self._tk_pic.bind_all("<Return>",       self._cb_save_active_image)
        self._tk_pic.bind_all("<Control-s>",    self._cb_save_active_image_as)

        self.set_active_size(init_size)
        self.set_lfp_paths(lfp_paths)

        # Main loop
        self._tk_root.mainloop()

    def quit(self, event=None):
        self._tk_root.destroy()
        self._tk_root.quit()

    def quit_force(self, event=None):
        self.quit()
        sys.exit()


    ################################
    # Pictures

    def set_lfp_paths(self, lfp_paths):
        if lfp_paths is not None and not lfp_paths:
            print "Select an LFP Picture file..."
            lfp_paths = tkFileDialog.askopenfilename(
                    title="Open an LFP Picture...",
                    filetypes=[ ('LFP Picture', '.lfp'), ],
                    multiple=True,
                    defaultextension=".lfp")
            if not lfp_paths:
                self.quit()
        self._lfp_paths = lfp_paths
        if self._lfp_paths:
            self.set_active_lfp(0)

    def set_active_lfp(self, lfp_id):
        if 0 <= lfp_id < len(self._lfp_paths):
            self._active_lfp_id = lfp_id
            self.set_lfp_path(self._lfp_paths[lfp_id])

    def _get_lfp_picture(self, lfp_path):
        if lfp_path not in self._lfp_picture_cache:
            new_lfp = LfpPictureFile(lfp_path)
            new_lfp.load()
            new_lfp.preload_pil_images()
            self._lfp_picture_cache[lfp_path] = new_lfp
        return self._lfp_picture_cache[lfp_path]

    def set_lfp_path(self, lfp_path):
        self._lfp = self._get_lfp_picture(lfp_path)
        self.set_title(
            file_path = self._lfp.file_path,
            file_name = self._lfp.file_name,
            index     = self._active_lfp_id + 1,
            count     = len(self._lfp_paths)
            )

        # Verify and init view
        if self._lfp.has_refocus_stack():
            self.show_refocus_lambda(self._lfp.get_default_lambda())
            #self.show_refocus_at(.5, .5)
            #self.show_all_focused()
        elif self._lfp.has_parallax_stack():
            self.show_parallax_at(.5, .5)
        else:
            raise Exception("Unsupported LFP Picture file")
        '''
        elif self._lfp.has_frame():
            #todo Processing raw data!
        '''

    def next_lfp(self, event=None):
        self.set_active_lfp(self._active_lfp_id + 1)

    def prev_lfp(self, event=None):
        self.set_active_lfp(self._active_lfp_id - 1)


    ################################
    # Title

    def set_title(self, **title_args):
        self._tk_root.wm_title(self._title_pattern.format(**title_args))

    ################################
    # Size

    def set_active_size(self, size):
        if size == self._active_size:
            return
        self._active_size = size
        self._reset_image_caches()
        self._redraw_active_image()

    def _cb_resize(self, event):
        new_size = (min(event.width, event.height), )*2
        self.set_active_size(new_size)


    ################################
    # Active Image

    def set_active_image(self, group, image_id):
        pil_image = self._lfp.get_pil_image(group, image_id)
        self.set_active_pil_image(pil_image)

    def set_active_pil_image(self, pil_image=None):
        if self._active_pil_image == pil_image:
            return
        self._active_pil_image = pil_image
        self._redraw_active_image()

    def _redraw_active_image(self):
        if not self._active_pil_image:
            return
        tkp_image = self._get_resized_tkp_image(self._active_pil_image)
        self._tk_pic.configure(image=tkp_image)

    def save_active_image(self, exp_path=None, exp_format='jpeg'):
        if not exp_path:
            exp_i = 0
            while os.path.exists(self._lfp.get_export_path('%03d'%exp_i, exp_format)):
                exp_i += 1
            exp_path = self._lfp.get_export_path('%03d'%exp_i, exp_format)
        print "Save image to %s" % exp_path
        self._active_pil_image.save(exp_path, exp_format)

    def _cb_save_active_image(self, event):
        self.save_active_image()

    def _cb_save_active_image_as(self, event):
        exp_path = tkFileDialog.asksaveasfilename(
                title="Save image as...",
                filetypes=[ ('JPEG', '.jpeg'), ('JPEG', '.jpg'), ],
                defaultextension=".jpeg")
        if not exp_path:
            return
        self.save_active_image(exp_path)


    ################################
    # PIL.Image/TK.PhotoImage Caches

    def _reset_image_caches(self):
        self._resized_pil_cache = {}
        self._resized_tkp_cache = {}

    def _get_resized_tkp_image(self, pil_image):
        if pil_image not in self._resized_tkp_cache:
            resized_pil_image = self._get_resized_pil_image(pil_image)
            self._resized_tkp_cache[pil_image] = TkPIL.PhotoImage(resized_pil_image)
        return self._resized_tkp_cache[pil_image]

    def _get_resized_pil_image(self, pil_image):
        if pil_image not in self._resized_pil_cache:
            self._resized_pil_cache[pil_image] = pil_image.resize(self._active_size, PIL.ANTIALIAS)
        return self._resized_pil_cache[pil_image]


    ################################
    # Refocus

    def show_refocus_at(self, x_f, y_f):
        if not self._lfp or not self._lfp.has_refocus_stack():
            return
        closest_refocus = self._lfp.find_closest_refocus_image(x_f, y_f)
        self._active_refocus_lambda = closest_refocus.lambda_
        self.set_active_image('refocus', closest_refocus.id)

    def _cb_refocus_at(self, event):
        self.show_refocus_at(
                event.x / self._active_size[0],
                event.y / self._active_size[1])

    def show_refocus_lambda(self, lambda_):
        if not self._lfp or not self._lfp.has_refocus_stack():
            return
        lambda_ = max(self._lfp.get_min_lambda(), min(lambda_, self._lfp.get_max_lambda()))
        closest_refocus = self._lfp.find_closest_refocus_image_by_lambda(lambda_)
        self._active_refocus_lambda = lambda_
        self.set_active_image('refocus', closest_refocus.id)

    def _cb_refocus_farther(self, event):
        new_lambda = self._active_refocus_lambda + .5
        self.show_refocus_lambda(new_lambda)

    def _cb_refocus_closer(self, event):
        new_lambda = self._active_refocus_lambda - .5
        self.show_refocus_lambda(new_lambda)


    ################################
    # All-Focused

    def show_all_focused(self):
        if not self._lfp or not self._lfp.has_refocus_stack():
            return
        self.set_active_image('all_focused', None)

    def _cb_all_focused(self, event):
        self.show_all_focused()


    ################################
    # Parallax

    def show_parallax_at(self, x_f, y_f):
        if not self._lfp or not self._lfp.has_parallax_stack():
            return
        x_f = max(0, min(x_f, 1))
        y_f = max(0, min(y_f, 1))
        closest_parallax = self._lfp.find_closest_parallax_image(x_f, y_f)
        self._active_parallax_viewp = (x_f, y_f)
        self.set_active_image('parallax', closest_parallax.id)

    def _cb_parallax_at(self, event):
        self.show_parallax_at(
                event.x / self._active_size[0],
                event.y / self._active_size[1])

    def _cb_parallax_left(self, event):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0] - .1, vp[1])
    def _cb_parallax_right(self, event):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0] + .1, vp[1])
    def _cb_parallax_up(self, event):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0], vp[1] + .1)
    def _cb_parallax_down(self, event):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0], vp[1] - .1)

