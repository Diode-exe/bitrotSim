"""Backward-compatible shift-only wrapper."""

from .main import VideoMod


class BitShift(VideoMod):
    """Compatibility wrapper exposing the historical shift-only class."""

    def __init__(self, video=None, bit_flip_count=1000, output_dir="output"):
        super().__init__(video=video, bit_flip_count=bit_flip_count, output_dir=output_dir)
