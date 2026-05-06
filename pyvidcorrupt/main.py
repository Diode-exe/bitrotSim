"""Public package API and CLI for corrupting video bytes."""

from __future__ import annotations

import argparse
import random
from pathlib import Path


class VideoMod:
    """Handle byte-level video corruption and output generation."""

    def __init__(self, video=None, bit_flip_count=1000, output_dir="output", quiet=False):
        self.video = video
        self.amount_of_files = 0
        self.bit_flip_count = bit_flip_count
        self.new_video = None
        self.output_dir = Path(output_dir)
        self.quiet = quiet
        self.source_path = None

    def assign_vid(self, video="video.mp4"):
        """Read a video file and assign it to the instance."""
        self.source_path = Path(video)
        with self.source_path.open("rb") as file_handle:
            self.video = file_handle.read()
        return self.video

    def _next_output_path(self, prefix):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.amount_of_files = len(list(self.output_dir.iterdir()))
        source_name = self.source_path.stem if self.source_path else "video"
        return self.output_dir / (
            f"{prefix}{self.bit_flip_count}_{source_name}{self.amount_of_files}.mp4"
        )

    def _write_output(self, modified_video, prefix, message):
        out_path = self._next_output_path(prefix)
        with out_path.open("wb") as file_handle:
            file_handle.write(modified_video)
        self.new_video = str(out_path)
        if not self.quiet:
            print(f"{message}: {self.new_video}")
        return self.new_video

    def mod_vid(self):
        """Modify the video by changing random bytes and save it."""
        if self.video is None:
            if not self.quiet:
                print("No video assigned.")
            return None

        modified_video = bytearray(self.video)
        for _ in range(self.bit_flip_count):
            index = random.randint(0, len(modified_video) - 1)
            modified_video[index] = random.randint(0, 255)

        return self._write_output(modified_video, "modified", "Modified video saved")

    def shift_vid(self):
        """Shift random byte values left or right and save the result."""
        if self.video is None:
            if not self.quiet:
                print("No video assigned.")
            return None

        modified_video = bytearray(self.video)
        for _ in range(self.bit_flip_count):
            index = random.randint(0, len(modified_video) - 1)
            value = modified_video[index]
            shift = random.randint(1, 7)
            if random.choice([True, False]):
                new_value = (value << shift) & 0xFF
            else:
                new_value = value >> shift
            modified_video[index] = new_value

        return self._write_output(modified_video, "shifted", "Shifted video saved")

def run_iterations(
    video_path="video.mp4",
    iterations=250,
    mode="shift",
    chain=False,
    bit_flip_count=250,
    output_dir="output",
    seed=None,
    print_seed=False,
    quiet=False,
):
    """Run the selected corruption mode repeatedly."""
    if seed is None:
        # If the user requested printing the seed, choose a reproducible
        # integer seed from system entropy and apply it so the run is
        # repeatable and the printed value actually represents the seed.
        if print_seed:
            seed = random.SystemRandom().randint(0, 2**32 - 1)
            random.seed(seed)
            print(f"Using random seed: {seed}")
        # Otherwise leave the global RNG unseeded (system entropy)
    else:
        random.seed(seed)
        if print_seed:
            print(f"Using chosen seed: {seed}")
    video_mod = VideoMod(bit_flip_count=bit_flip_count, output_dir=output_dir, quiet=quiet)
    video_mod.assign_vid(video_path)

    for _ in range(iterations):
        if chain and video_mod.new_video:
            video_mod.assign_vid(video_mod.new_video)

        if mode == "random":
            video_mod.new_video = video_mod.mod_vid()
        else:
            video_mod.new_video = video_mod.shift_vid()

    return video_mod.new_video


def build_parser():
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Corrupt a video by random byte edits.")
    parser.add_argument("video", nargs="?", default="video.mp4", help="Input video path")
    parser.add_argument(
        "--mode",
        choices=["random", "shift"],
        default="shift",
        help="Corruption mode to apply",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=250,
        help="Number of files to generate",
    )
    parser.add_argument(
        "--bit-flip-count",
        type=int,
        default=250,
        help="Number of random byte positions to modify per output",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory where generated files are written",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Integer seed for the random number generator (reproducible results)",
    )
    parser.add_argument(
        "--print-seed",
        action="store_true",
        help="Print the random seed used (for reproducibility)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output messages about generated files",
    )
    parser.add_argument(
        "--chain",
        action="store_true",
        help="Use each generated file as the input for the next iteration",
    )
    return parser


def main(argv=None):
    """Run the package CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    run_iterations(
        video_path=args.video,
        iterations=args.iterations,
        mode=args.mode,
        chain=args.chain,
        bit_flip_count=args.bit_flip_count,
        output_dir=args.output_dir,
        seed=args.seed,
        print_seed=args.print_seed,
        quiet=args.quiet,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
