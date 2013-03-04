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


from __future__ import division, print_function

import sys

import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")

# Handle gstreamer-python bug with command-line help options
# https://bugzilla.gnome.org/show_bug.cgi?id=549879
__argv, sys.argv = sys.argv, filter(lambda arg: arg not in ('-h', '--help'), sys.argv)
import gst
sys.argv = __argv


################################################################
# Memory Source

class MemSrc(gst.BaseSrc):
    """A GStreamer Source reading from memory
    """

    __gsttemplates__ = (
            gst.PadTemplate("src",
                gst.PAD_SRC,
                gst.PAD_ALWAYS,
                gst.caps_new_any()),
            )

    def __init__(self, name):
        self.__gobject_init__()
        self._data = None
        self.set_name(name)

    def set_property(self, name, value):
        if name == 'data':
            self._data = value
            self._data_len = len(value)

    def do_create(self, offset, size):
        size = 4096 * 2**4
        if self._data and offset < self._data_len:
            blob = self._data[offset:offset+size]
            return gst.FLOW_OK, gst.Buffer(blob)
        else:
            return gst.FLOW_UNEXPECTED, None

gobject.type_register(MemSrc)


################################################################
# Multi Memory Sink

class MultiMemSink(gst.BaseSink):
    """A GStreamer Sink writing buffers to a list in memory
    """

    __gsttemplates__ = (
            gst.PadTemplate("sink",
                gst.PAD_SINK,
                gst.PAD_ALWAYS,
                gst.caps_new_any()),
            )

    def __init__(self, name):
        self.__gobject_init__()
        self._data_list = []
        self.set_name(name)

    def get_property(self, name):
        if name == 'data_list':
            return self._data_list

    def do_render(self, bfr):
        self._data_list.append(bfr)
        return gst.FLOW_OK

gobject.type_register(MultiMemSink)


################################################################
# Splitter

class H246Splitter:
    """A standalone H264 video splitter

    Supported export image formats: JPEG, PNG
    """

    mainloop = gobject.MainLoop()

    def __init__(self, input_data, image_format='jpeg'):
        if image_format not in ('jpeg', 'png'):
            raise Exception("Format not supported: %s" % image_format)

        self._input_data = input_data
        self._output_images = None

        # Create pipeline
        self.pipeline_desc = ("""
            h264parse name=head
            ! ffdec_h264
            ! deinterlace
            ! gamma gamma=0.6
            ! ffmpegcolorspace
            ! video/x-raw-rgb,depth=24
            ! %senc name=tail
            """ % image_format)
        self.pipeline = gst.parse_launch(self.pipeline_desc)

        # Set source
        self.mem_src = MemSrc('my_src')
        self.mem_src.set_property('data', self._input_data)
        self.pipeline.add(self.mem_src)
        self.mem_src.link(self.pipeline.get_by_name('head'))

        # Set sink
        self.multi_mem_sink = MultiMemSink('my_sink')
        self.pipeline.add(self.multi_mem_sink)
        self.pipeline.get_by_name('tail').link(self.multi_mem_sink)

    def get_images(self):
        if not self._output_images:
            self.pipeline.set_state(gst.STATE_PLAYING)
            bus = self.pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message::eos",   self._cb_bus_eos)
            bus.connect("message::error", self._cb_bus_error)
            self.mainloop.run()
            self.pipeline.set_state(gst.STATE_NULL)
            self._output_images = self.multi_mem_sink.get_property('data_list')
        return self._output_images

    def _cb_bus_eos(self, bus, msg):
        self.mainloop.quit()

    def _cb_bus_error(self, bus, msg):
        err, debug = msg.parse_error()
        self.mainloop.quit()
        raise Exception("Error: %s" % err, debug)


################################################################
# Test

def _split_file(file_path, image_format='jpeg'):
    print("H264 file: %s" % file_path)
    input_data = open(file_path).read()
    splitter = H246Splitter(input_data, image_format)
    images = splitter.get_images()
    for idx, img in enumerate(images):
        output_name = '%s__%05d.%s' % (file_path, idx, image_format)
        print("Create JPEG file: %s" % output_name)
        with file(output_name, 'w') as f:
            f.write(img)

if __name__=='__main__':
    if len(sys.argv) not in (2, 3):
        print("Usage: %s [h264-encoded.data]" % sys.argv[0])
        sys.exit(1)
    _split_file(*sys.argv[1:])

