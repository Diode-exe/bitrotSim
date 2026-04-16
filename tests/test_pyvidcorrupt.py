import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from pyvidcorrupt import VideoMod, run_iterations


class PyVidCorruptTests(unittest.TestCase):
    def test_mod_vid_writes_output(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.mp4"
            source.write_bytes(bytes(range(64)))

            video_mod = VideoMod(bit_flip_count=5, output_dir=root / "output")
            video_mod.assign_vid(source)
            output_path = video_mod.mod_vid()

            self.assertIsNotNone(output_path)
            self.assertTrue(Path(output_path).exists())
            self.assertEqual(len(Path(output_path).read_bytes()), 64)

    def test_shift_vid_writes_output(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.mp4"
            source.write_bytes(bytes(range(64)))

            video_mod = VideoMod(bit_flip_count=5, output_dir=root / "output")
            video_mod.assign_vid(source)
            output_path = video_mod.shift_vid()

            self.assertIsNotNone(output_path)
            self.assertTrue(Path(output_path).exists())
            self.assertEqual(len(Path(output_path).read_bytes()), 64)

    def test_run_iterations_returns_last_output(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "sample.mp4"
            source.write_bytes(bytes(range(64)))

            output_path = run_iterations(
                video_path=source,
                iterations=2,
                mode="shift",
                bit_flip_count=5,
                output_dir=root / "output",
            )

            self.assertIsNotNone(output_path)
            self.assertTrue(Path(output_path).exists())


if __name__ == "__main__":
    unittest.main()
