#!/usr/bin/env python
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


"""View LFP Picture files with refocus and parallax support
"""


import os, os.path
import sys
from cStringIO import StringIO

import Tkinter, tkFileDialog

from lfp_reader.tk_lfp_viewer import TkLfpViewer


def main(file_dir_paths):
    lfp_paths = []
    for x in file_dir_paths:
        if os.path.isdir(x):
            lfp_paths.extend(os.path.join(x, y) for y in os.listdir(x)
                    if os.path.isfile(os.path.join(x, y))
                    and os.path.join(x, y).lower().endswith('-stk.lfp'))
        else:
            lfp_paths.append(x)
    viewer = TkLfpViewer(lfp_paths)
    viewer.bind_all('<Control-q>',   viewer.destroy_quit_exit)
    viewer.mainloop()


def usage(errcode=0, of=sys.stderr):
    print >>of, ("Usage: %s picture-stk.lfp [picture-stk-2.lfp ...]" %
            os.path.basename(sys.argv[0]))
    sys.exit(errcode)


if __name__=='__main__':
    if len(sys.argv) < 1:
        usage(1)
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(2)
    except Exception as err:
        print >>sys.stderr, "Error:", err
        if sys.platform == 'win32': raw_input()
        sys.exit(9)

