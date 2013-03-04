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


from __future__ import division, print_function

import sys
import os.path
import re
import webbrowser

from .lfp_picture import LfpPictureFile
from .lfp_logging import log
from ._utils import (
        pil, piltk, check_pil_module,
        tk, tkFileDialog )



################################################################

class TkLfpViewer(tk.Tk):
    """View and refocues Processed LFP Picture files
    """

    def __init__(self,
            lfp_paths=None,
            title_pattern="{file_path}   ({index}/{count})   Python LFP Reader",
            init_size=(540, 540),
            *args, **kwargs):

        check_pil_module()
        self._title_pattern = title_pattern
        self._lfp_picture_cache = {}
        self._lfp = None
        self._active_size = None
        self._active_pil_image = None
        self._active_refocus_lambda = None
        self._active_parallax_viewp = (.5, .5)

        # Create tk window
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.protocol
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.geometry("%dx%d" % init_size)
        self.config(background='black')
        self.wm_title("Python LFP Reader")
        # window
        self.bind('<Configure>',    self._cb_config)
        self.bind('<Control-q>',    self._cb_quit)
        # navigation: next
        self.bind("<Right>",        self.next_lfp)
        self.bind("<n>",            self.next_lfp)
        self.bind("<space>",        self.next_lfp)
        # navigation: previous
        self.bind("<Left>",         self.prev_lfp)
        self.bind("<p>",            self.prev_lfp)
        self.bind("<BackSpace>",    self.prev_lfp)
        # image: refocuse by lambda
        self.bind("<Up>",            self._cb_refocus_farther)
        self.bind("<Down>",          self._cb_refocus_closer)
        # image: all focused
        self.bind("<Escape>",        self._cb_all_focused)
        # image: parallax
        self.bind("<a>",             self._cb_parallax_left)
        self.bind("<d>",             self._cb_parallax_right)
        self.bind("<w>",             self._cb_parallax_up)
        self.bind("<s>",             self._cb_parallax_down)
        # image: open/export
        self.bind('<Control-w>',     self._cb_close_lfp)
        self.bind("<Control-o>",     self._cb_open_files)
        self.bind("<Control-s>",     self._cb_export_active_image_as)
        self.bind("<Return>",        self._cb_export_active_image)

        # Create tk picture
        self._pic = tk.Label(self)
        self._pic.pack()
        # image: refocuse by click
        self._pic.bind    ("<Button-1>",    self._ms_refocus_at)
        self._pic.bind_all("<B1-Motion>",   self._ms_refocus_at)
        # image: refocuse by lambda
        self._pic.bind_all("<Button-4>",    self._cb_refocus_farther)
        self._pic.bind_all("<Button-5>",    self._cb_refocus_closer)
        # image: all focused
        self._pic.bind_all("<Button-2>",    self._cb_all_focused)
        # image: parallax
        self._pic.bind_all("<Button-3>",    self._ms_parallax_at)
        self._pic.bind_all("<B3-Motion>",   self._ms_parallax_at)

        # Create menubar
        self._init_menu()

        self.set_active_size(init_size)
        self.set_lfp_paths(lfp_paths)

    def _cb_config(self, event=None):
        new_size = (min(event.width, event.height), )*2
        self.set_active_size(new_size)

    def _cb_quit(self, event=None):
        self.quit()


    ################################
    # Menu

    def _init_menu(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="LFP Viewer",
                menu=filemenu)
        filemenu.add_command(label="Open...",
                command=self._cb_open_files,
                accelerator="Ctrl+O")
        filemenu.add_command(label="JPEG Export",
                command=self._cb_export_active_image,
                accelerator="Enter")
        filemenu.add_command(label="JPEG Export as...",
                command=self._cb_export_active_image_as,
                accelerator="Ctrl+S")
        filemenu.add_command(label="Close",
                command=self._cb_close_lfp,
                accelerator="Ctrl+W")
        filemenu.add_separator()
        filemenu.add_command(label="Exit",
                command=self.quit,
                accelerator="Ctrl+Q")

        viewmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View",
                menu=viewmenu)
        viewmenu.add_command(label="Next Picture",
                command=self.next_lfp,
                accelerator="Right-Arrow")
        viewmenu.add_command(label="Previous Picture",
                command=self.prev_lfp,
                accelerator="Left-Arrow")
        viewmenu.add_separator()
        viewmenu.add_command(label="Refocuse",
                command=self.show_refocus,
                accelerator="Left-Click")
        viewmenu.add_command(label="All-Focused",
                command=self.show_all_focused,
                accelerator="Middle-Click")
        viewmenu.add_command(label="Parallax",
                command=self.show_parallax,
                accelerator="Right-Click")

        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="About",
                menu=helpmenu)
        helpmenu.add_command(label="Project Homepage",
                command=lambda: webbrowser.open('http://code.behnam.es/python-lfp-reader'))

        menubar.add_command(label="")

        self.config(menu=menubar)
        self._menubar = menubar

    def _start_loading(self):
        self._menubar.entryconfig(4, label="Loading...")

    def _end_loading(self):
        self._menubar.entryconfig(4, label="")


    ################################
    # Pictures

    def set_lfp_paths(self, lfp_paths):
        if lfp_paths is not None and not lfp_paths:
            log("Select LFP Pictures...")
            lfp_paths = self._open_files()
            if not lfp_paths:
                self.quit()
        self._lfp_paths = lfp_paths
        self.set_active_lfp(0)

    def _cb_open_files(self, event=None):
        lfp_paths = self._open_files()
        if lfp_paths:
            n = len(self._lfp_paths)
            self._lfp_paths.extend(lfp_paths)
            self.set_active_lfp(n)

    def _open_files(self):
        paths = tkFileDialog.askopenfilename(
                title="Open LFP Pictures...",
                filetypes=[ ('LFP Picture', '.lfp'), ],
                multiple=True,
                defaultextension=".lfp")
        if isinstance(paths, (unicode, str)):
            # Handle an old Python-TCL bug
            return [ re.sub("^{|}$", "", i)
                    for i in re.findall("{.*?}|\S+", paths) ]
        else:
            return paths

    def _cb_close_lfp(self, event=None):
        if 1 < len(self._lfp_paths):
            self._lfp_paths.pop(self._active_lfp_id)
            self.set_active_lfp(self._active_lfp_id-1 if self._active_lfp_id > 0 else 0)

    def set_active_lfp(self, lfp_id):
        if 0 <= lfp_id < len(self._lfp_paths):
            self._active_lfp_id = lfp_id
            self.set_lfp_path(lfp_id)

    def _get_lfp_picture(self, lfp_path):
        if lfp_path not in self._lfp_picture_cache:
            new_lfp = LfpPictureFile(lfp_path)
            new_lfp.load()
            self.update()
            new_lfp.preload_pil_images()
            self._lfp_picture_cache[lfp_path] = new_lfp
        return self._lfp_picture_cache[lfp_path]

    def set_lfp_path(self, lfp_id):
        lfp_path = self._lfp_paths[lfp_id]
        self.set_title(
            file_path = lfp_path,
            index     = lfp_id + 1,
            count     = len(self._lfp_paths)
            )
        self._start_loading()
        self.update()
        self._lfp = self._get_lfp_picture(lfp_path)
        self._end_loading()

        # Verify and init view
        if self._lfp.has_refocus_stack():
            self.show_refocus()
        elif self._lfp.has_parallax_stack():
            self.show_parallax()
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
        self.wm_title(self._title_pattern.format(**title_args))

    ################################
    # Size

    def set_active_size(self, size):
        if size == self._active_size:
            return
        self._active_size = size
        self._reset_image_caches()
        self._start_loading()
        self._redraw_active_image()
        self._end_loading()


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
        self._pic.config(image=tkp_image)

    def export_active_image(self, exp_path=None, exp_format='jpeg'):
        if not exp_path:
            exp_i = 0
            while os.path.exists(self._lfp.get_export_path('%03d'%exp_i, exp_format)):
                exp_i += 1
            exp_path = self._lfp.get_export_path('%03d'%exp_i, exp_format)
        log("Save JPEG image to %s" % exp_path)
        self._active_pil_image.save(exp_path, exp_format)

    def _cb_export_active_image(self, event=None):
        self.export_active_image()

    def _cb_export_active_image_as(self, event=None):
        exp_path = tkFileDialog.asksaveasfilename(
                title="Save JPEG image as...",
                filetypes=[ ('JPEG', '.jpeg'), ('JPEG', '.jpg'), ],
                defaultextension=".jpeg")
        if not exp_path:
            return
        self.export_active_image(exp_path)


    ################################
    # pil.Image/tk.PhotoImage Caches

    def _reset_image_caches(self):
        self._resized_pil_cache = {}
        self._resized_tkp_cache = {}

    def _get_resized_tkp_image(self, pil_image):
        if pil_image not in self._resized_tkp_cache:
            resized_pil_image = self._get_resized_pil_image(pil_image)
            self._resized_tkp_cache[pil_image] = piltk.PhotoImage(resized_pil_image)
        return self._resized_tkp_cache[pil_image]

    def _get_resized_pil_image(self, pil_image):
        if pil_image not in self._resized_pil_cache:
            self._resized_pil_cache[pil_image] = pil_image.resize(self._active_size, pil.ANTIALIAS)
        return self._resized_pil_cache[pil_image]


    ################################
    # Refocus

    def show_refocus(self):
        if self._active_refocus_lambda is None:
            self._active_refocus_lambda = self._lfp.get_default_lambda()
        self.show_refocus_lambda(self._active_refocus_lambda)

    def show_refocus_at(self, x_f, y_f):
        if not self._lfp or not self._lfp.has_refocus_stack():
            return
        closest_refocus = self._lfp.find_closest_refocus_image(x_f, y_f)
        self._active_refocus_lambda = closest_refocus.lambda_
        self.set_active_image('refocus', closest_refocus.id)

    def _ms_refocus_at(self, event=None):
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

    def _cb_refocus_farther(self, event=None):
        new_lambda = self._active_refocus_lambda + .5
        self.show_refocus_lambda(new_lambda)

    def _cb_refocus_closer(self, event=None):
        new_lambda = self._active_refocus_lambda - .5
        self.show_refocus_lambda(new_lambda)


    ################################
    # All-Focused

    def show_all_focused(self):
        if not self._lfp or not self._lfp.has_refocus_stack():
            return
        self.set_active_image('all_focused', None)

    def _cb_all_focused(self, event=None):
        self.show_all_focused()


    ################################
    # Parallax

    def show_parallax(self):
        if self._active_parallax_viewp is None:
            self._active_parallax_viewp = (.5, .5)
        self.show_parallax_at(*self._active_parallax_viewp)

    def show_parallax_at(self, x_f, y_f):
        if not self._lfp or not self._lfp.has_parallax_stack():
            return
        x_f = max(0, min(x_f, 1))
        y_f = max(0, min(y_f, 1))
        closest_parallax = self._lfp.find_closest_parallax_image(x_f, y_f)
        self._active_parallax_viewp = (x_f, y_f)
        self.set_active_image('parallax', closest_parallax.id)

    def _ms_parallax_at(self, event=None):
        self.show_parallax_at(
                event.x / self._active_size[0],
                event.y / self._active_size[1])

    def _cb_parallax_left(self, event=None):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0] - .1, vp[1])
    def _cb_parallax_right(self, event=None):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0] + .1, vp[1])
    def _cb_parallax_up(self, event=None):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0], vp[1] + .1)
    def _cb_parallax_down(self, event=None):
        vp = self._active_parallax_viewp
        self.show_parallax_at(vp[0], vp[1] - .1)

