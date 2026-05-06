import cv2
import random
import numpy as np

class RandomGray:
    """Write randomized visual effects into a video.

    Modes:
    - "luma": modify only the luma (Y) channel and neutralize chroma so patches desaturate correctly.
    - "blocky": paint macroblocks filled with their mean color to simulate compression blocking.
    - "bitflip": encode each frame to JPEG, flip random bits in the encoded bytes, then decode
      to produce unpredictable glitch artifacts.
    """

    def __init__(self):
        pass

    def write_random_gray(
        self,
        src: str,
        out: str,
        mode: str = "luma",
        patches_per_frame: int = 3,
        max_patch_frac: float = 1 / 3,
        block_sizes=(8, 16, 32),
        bitflip_bytes: int = 200,
    ) -> None:
        cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            raise RuntimeError(f"Could not open source: {src}")

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(out, fourcc, fps, (w, h))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if mode == "luma":
                # Work in YCrCb: channel 0 is Y, 1 is Cr, 2 is Cb
                ycc = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
                for _ in range(patches_per_frame):
                    rw = random.randint(20, max(20, int(w * max_patch_frac)))
                    rh = random.randint(20, max(20, int(h * max_patch_frac)))
                    x = random.randint(0, max(0, w - rw))
                    y = random.randint(0, max(0, h - rh))
                    gray = random.randint(0, 255)
                    ycc[y : y + rh, x : x + rw, 0] = gray
                    # neutralize chroma so patch becomes achromatic
                    ycc[y : y + rh, x : x + rw, 1] = 128
                    ycc[y : y + rh, x : x + rw, 2] = 128
                frame = cv2.cvtColor(ycc, cv2.COLOR_YCrCb2BGR)

            elif mode == "blocky":
                for _ in range(patches_per_frame * 2):
                    bs = random.choice(block_sizes)
                    rw = bs
                    rh = bs
                    x = random.randint(0, max(0, w - rw))
                    y = random.randint(0, max(0, h - rh))
                    block = frame[y : y + rh, x : x + rw]
                    if block.size == 0:
                        continue
                    mean_color = block.mean(axis=(0, 1)).astype(np.uint8)
                    frame[y : y + rh, x : x + rw] = mean_color

            elif mode == "bitflip":
                # encode to jpeg bytes, flip random bits, then try to decode
                try:
                    ok, buf = cv2.imencode(".jpg", frame)
                    if ok:
                        data = bytearray(buf.tobytes())
                        n = min(len(data), bitflip_bytes)
                        for _ in range(n):
                            idx = random.randrange(len(data))
                            bit = 1 << random.randint(0, 7)
                            data[idx] ^= bit
                        arr = np.frombuffer(data, dtype=np.uint8)
                        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                        if img is not None:
                            frame = img
                except Exception:
                    # on any failure, keep original frame
                    pass

            else:
                raise ValueError(f"Unknown mode: {mode}")

            writer.write(frame)

        cap.release()
        writer.release()


if __name__ == "__main__":
    # Example usage: change `mode` to 'luma', 'blocky', or 'bitflip'
    rg = RandomGray()
    # default writes luma-based desaturation patches
    rg.write_random_gray("video.mp4", "output_video.mp4", mode="blocky")