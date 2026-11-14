from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parent

INPUT = (
    PROJECT_ROOT
    / "data"
    / "terrain"
    / "lola"
    / "ldem_85s_40m_float.img"
)

OUTPUT = (
    PROJECT_ROOT
    / "assets"
    / "maps"
    / "moon_height_map.png"
)

ROWS = 7584
COLUMNS = 7584

print("Loading LOLA DEM...")

data = np.memmap(
    INPUT,
    dtype="<f4",
    mode="r",
    shape=(ROWS, COLUMNS),
)

height = np.asarray(data, dtype=np.float32)

print(f"DEM shape: {height.shape}")
print(f"DEM min:   {np.nanmin(height):.6f} km")
print(f"DEM max:   {np.nanmax(height):.6f} km")

# Convert NaN/invalid values into masked data.
masked = np.ma.masked_invalid(height)

# Robust display range.
# This prevents a few extreme pixels from destroying
# the visual contrast of the entire map.
low = float(np.percentile(masked.compressed(), 2))
high = float(np.percentile(masked.compressed(), 98))

print(f"Display range: {low:.6f} km -> {high:.6f} km")

plt.figure(figsize=(10, 10), dpi=150)

plt.imshow(
    masked,
    origin="upper",
    cmap="terrain",
    vmin=low,
    vmax=high,
)

plt.axis("off")

plt.tight_layout(pad=0)

plt.savefig(
    OUTPUT,
    dpi=150,
    bbox_inches="tight",
    pad_inches=0,
)

plt.close()

print()
print("HEIGHT MAP CREATED")
print(f"Output: {OUTPUT}")
print(f"Size:   {OUTPUT.stat().st_size} bytes")
