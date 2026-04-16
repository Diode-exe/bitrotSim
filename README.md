# pyvidcorrupt

`pyvidcorrupt` is a small installable package for generating corrupted video outputs by either replacing random bytes or shifting random byte values.

## Install

```bash
pip install -e .
```

## CLI usage

```bash
pyvidcorrupt dmvsource.mp4 --mode shift --iterations 10
python -m pyvidcorrupt dmvsource.mp4 --mode random --iterations 5 --output-dir output
```

## Python usage

```python
from pyvidcorrupt import VideoMod, run_iterations

video_mod = VideoMod(bit_flip_count=1000, output_dir="output")
video_mod.assign_vid("dmvsource.mp4")
video_mod.shift_vid()

run_iterations("dmvsource.mp4", iterations=10, mode="random")
```

## Notes

- `--mode shift` applies left or right bit shifting to random byte positions.
- `--mode random` replaces random byte positions with random byte values.
- `--chain` uses each generated output as the next iteration's input.
