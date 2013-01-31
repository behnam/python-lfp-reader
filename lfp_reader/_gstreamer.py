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


import gobject
gobject.threads_init()
import pygst
pygst.require("0.10")
import gst


################################
# Memory Source

class MemSrc(gst.BaseSrc):

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

    def do_create(self, offset, size):
        if self._data and offset < len(self._data):
            blob = self._data[offset:offset+size]
            return gst.FLOW_OK, gst.Buffer(blob)
        else:
            return gst.FLOW_UNEXPECTED, None

gobject.type_register(MemSrc)


################################
# Memory Sink

class MultiMemSink(gst.BaseSink):

    __gsttemplates__ = (
            gst.PadTemplate("sink",
                gst.PAD_SINK,
                gst.PAD_ALWAYS,
                gst.caps_new_any()),
            )

    def __init__(self, name):
        self.__gobject_init__()
        self._data = []
        self.set_name(name)

    def get_property(self, name):
        if name == 'data':
            return self._data

    def do_render(self, bfr):
        if self._data is not None:
            self._data.append(bfr)
            return gst.FLOW_OK
        else:
            return gst.FLOW_UNEXPECTED

gobject.type_register(MultiMemSink)



################################
# Splitter

class H246Splitter:
    mainloop = gobject.MainLoop()

    def __init__(self, input_data, image_format='jpeg'):
        if image_format not in ('jpeg', 'png'):
            raise Exception("Format not supported: %s" % image_format)

        self.input_data = input_data
        self.images = None

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
        self.mem_src.set_property('data', input_data)
        self.pipeline.add(self.mem_src)
        self.mem_src.link(self.pipeline.get_by_name('head'))

        # Set sink
        self.multi_mem_sink = MultiMemSink('my_sink')
        self.pipeline.add(self.multi_mem_sink)
        self.pipeline.get_by_name('tail').link(self.multi_mem_sink)

    #todo Find a way to not intrupt gobject mainloop if already exists

    def get_images(self):
        if not self.images:
            self.pipeline.set_state(gst.STATE_PLAYING)
            self.pipeline.get_bus().add_watch(self.bus_event)
            self.mainloop.run()
            self.pipeline.set_state(gst.STATE_NULL)
            self.images = self.multi_mem_sink.get_property('data')
        return self.images

    def bus_event(self, bus, msg):
        if msg.type == gst.MESSAGE_EOS:
            self.mainloop.quit()
        elif msg.type == gst.MESSAGE_ERROR:
            err, debug = msg.parse_error()
            #print "Error: %s" % err, debug
            self.mainloop.quit()
        return True


if __name__=='__main__':
    import sys
    input_data = open(sys.argv[1]).read()
    h264splitter = H246Splitter(input_data)
    images = h264splitter.get_images()
    for idx, img in enumerate(images):
        output_name = '%s-%05d.jpeg' % (sys.argv[1], idx)
        open(output_name, 'w').write(img)

