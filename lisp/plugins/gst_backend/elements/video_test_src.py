# This file is part of Linux Show Player
#
# Copyright 2021 Francesco Ceruti <ceppofrancy@gmail.com>
#
# Linux Show Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Linux Show Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Linux Show Player.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtCore import QT_TRANSLATE_NOOP

from lisp.backend.media_element import ElementType, MediaType
from lisp.plugins.gst_backend import GstBackend
from lisp.plugins.gst_backend.gi_repository import Gst
from lisp.plugins.gst_backend.gst_element import GstMediaElement


class VideoTestSrc(GstMediaElement):
    ElementType = ElementType.Output
    MediaType = MediaType.Video
    Name = QT_TRANSLATE_NOOP("MediaElementName", "Video Test Source")

    FALLBACK_DEVICE = "default"

    def __init__(self, pipeline):
        super().__init__(pipeline)
        self.videotestsrc = Gst.ElementFactory.make("videotestsrc", "videotestsrc")
        self.autovideosink = Gst.ElementFactory.make("autovideosink", "sink")
        
        self.pipeline.add(self.videotestsrc)
        self.pipeline.add(self.autovideosink)
        
        self.device = GstBackend.Config.get("video_test_device", self.FALLBACK_DEVICE)
        self.changed("device").connect(self._update_device)

    def sink(self):
        return self.autovideosink

    def _update_device(self, new_device):
        # Remove and dispose element
        self.videotestsrc.unlink(self.autovideosink)
        self.pipeline.remove(self.autovideosink)
        self.autovideosink.set_state(Gst.State.NULL)

        # Create new element and add it to the pipeline
        self.autovideosink = Gst.ElementFactory.make("autovideosink", "sink")
        self.autovideosink.set_property("device", new_device)

        self.pipeline.add(self.autovideosink)
        self.videotestsrc.link(self.autovideosink)