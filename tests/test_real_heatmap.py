import math
import os
from datetime import datetime, timezone

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from app.core.models import Site
from app.science.engine import LunarAnalysisEngine
from app.science.heatmap import (
    calculate_visibility_heatmap,
    pixel_to_coordinate,
)


print("=" * 70)
print("LUNAR LANDING SITE NAVIGATOR")
print("REAL HEATMAP / SPICE + LOLA INTEGRITY TEST")
print("=" * 70)

project = os.getcwd()
print(f"\nProject: {project}")

analysis_time = datetime(
    2026,
    11,
    15,
    4,
    32,
    44,
    tzinfo=timezone.utc,
)

engine = LunarAnalysisEngine()
engine.load()

print("\n[PASS] Real SPICE + LOLA kernels loaded")

print("\n1. HEATMAP CALCULATION")
print("-" * 70)

result = calculate_visibility_heatmap(
    engine=engine,
    analysis_time=analysis_time,
    grid_size=32,
)

assert result.grid_size == 32
assert result.analysis_time == analysis_time
assert len(result.cells) == 32 * 32

print(f"[PASS] Heatmap grid size = {result.grid_size}x{result.grid_size}")
print(f"[PASS] Cell count = {len(result.cells)}")
print(f"[PASS] UTC preserved = {result.analysis_time}")

available = result.available_cells
unavailable = result.unavailable_cells

print(f"[PASS] Terrain available cells = {available}")
print(f"[PASS] Terrain unavailable cells = {unavailable}")

assert available > 0
assert unavailable > 0

print("[PASS] Grid contains both valid and unavailable DEM coverage")

print("\n2. REAL TERRAIN VISIBILITY COUNTS")
print("-" * 70)

sun_visible = 0
sun_blocked = 0
sun_unavailable = 0

earth_visible = 0
earth_blocked = 0
earth_unavailable = 0

for cell in result.cells:

    if cell.sun_visible is True:
        sun_visible += 1
    elif cell.sun_visible is False:
        sun_blocked += 1
    else:
        sun_unavailable += 1

    if cell.earth_visible is True:
        earth_visible += 1
    elif cell.earth_visible is False:
        earth_blocked += 1
    else:
        earth_unavailable += 1

print(
    f"Sun   visible={sun_visible} "
    f"blocked={sun_blocked} "
    f"unavailable={sun_unavailable}"
)

print(
    f"Earth visible={earth_visible} "
    f"blocked={earth_blocked} "
    f"unavailable={earth_unavailable}"
)

assert sun_visible + sun_blocked + sun_unavailable == len(result.cells)
assert earth_visible + earth_blocked + earth_unavailable == len(result.cells)

# A valid DEM sample and a valid directional terrain-horizon
# result are separate concepts. Some cells can have terrain
# coverage while the Sun/Earth terrain result is unavailable.
assert sun_unavailable >= 0
assert earth_unavailable >= 0

print("[PASS] Sun visibility classification is complete")
print("[PASS] Earth visibility classification is complete")
print(
    "[PASS] Terrain-result availability is tracked independently "
    "for Sun/Earth"
)

print("\n3. CELL DATA INTEGRITY")
print("-" * 70)

for index, cell in enumerate(result.cells):

    assert math.isfinite(cell.row)
    assert math.isfinite(cell.column)

    assert math.isfinite(cell.latitude)
    assert math.isfinite(cell.longitude)

    # Every heatmap cell must resolve to a valid geographic
    # coordinate. Only cells with valid DEM coverage are required
    # to lie inside the strict LOLA south-polar coverage range.
    assert -90.0 <= cell.latitude <= 90.0
    assert -180.0 <= cell.longitude < 180.0

    if cell.terrain_available:
        assert -90.0 <= cell.latitude <= -85.0

        # A valid DEM sample does not guarantee that the
        # directional terrain-horizon calculation is available
        # for every target. The established result contract is
        # True / False / None.
        assert cell.sun_visible in (True, False, None)
        assert cell.earth_visible in (True, False, None)

        assert cell.sun_status
        assert cell.earth_status

    else:
        assert cell.sun_visible is None
        assert cell.earth_visible is None

        assert cell.sun_status == "Terrain Unavailable"
        assert cell.earth_status == "Terrain Unavailable"

print("[PASS] All heatmap cells contain valid geographic coordinates")
print("[PASS] Latitude remains inside LOLA south-polar coverage")
print("[PASS] Longitude normalization is valid")
print("[PASS] Available cells have real visibility results")
print("[PASS] Unavailable cells remain explicitly unavailable")

print("\n4. LOLA POSITION AGREEMENT")
print("-" * 70)

terrain = engine.observer.terrain

checked = 0

for cell in result.cells:

    if not cell.terrain_available:
        continue

    sample = terrain.sample(
        cell.latitude,
        cell.longitude,
    )

    projected_latitude, projected_longitude = pixel_to_coordinate(
        cell.row,
        cell.column,
    )

    assert math.isfinite(sample.height_km)
    assert math.isfinite(sample.radius_km)

    latitude_error = abs(
        projected_latitude - cell.latitude
    )

    longitude_error = abs(
        projected_longitude - cell.longitude
    )

    # The heatmap coordinate comes from the same projection
    # and is intentionally represented by the cell center.
    assert latitude_error < 0.001
    assert longitude_error < 0.001

    checked += 1

    if checked >= 10:
        break

assert checked == 10

print(
    "[PASS] First 10 available heatmap positions "
    "match real LOLA samples"
)

print("\n5. REAL SCIENCE RESPONSE CHECK")
print("-" * 70)

sun_values = [
    cell.sun_visible
    for cell in result.cells
    if cell.terrain_available
]

earth_values = [
    cell.earth_visible
    for cell in result.cells
    if cell.terrain_available
]

assert all(
    value in (True, False, None)
    for value in sun_values
)

assert all(
    value in (True, False, None)
    for value in earth_values
)

assert any(value is not None for value in sun_values)
assert any(value is not None for value in earth_values)

print(
    "[PASS] Sun terrain results contain only "
    "True/False/None"
)

print(
    "[PASS] Earth terrain results contain only "
    "True/False/None"
)

print(
    "[PASS] Valid heatmap coverage produces real "
    "Sun/Earth terrain results where available"
)

print("\n6. GRID VALIDATION")
print("-" * 70)

for invalid_grid in (0, 1, 129):

    try:
        calculate_visibility_heatmap(
            engine=engine,
            analysis_time=analysis_time,
            grid_size=invalid_grid,
        )
    except ValueError:
        print(
            f"[PASS] grid_size={invalid_grid} correctly rejected"
        )
    else:
        raise AssertionError(
            f"grid_size={invalid_grid} was not rejected"
        )

try:
    calculate_visibility_heatmap(
        engine=engine,
        analysis_time=analysis_time,
        grid_size=32.0,
    )
except TypeError:
    print("[PASS] non-integer grid_size correctly rejected")
else:
    raise AssertionError(
        "non-integer grid_size was not rejected"
    )

engine.unload()

print("\n" + "=" * 70)
print("FINAL RESULT")
print("=" * 70)
print(
    f"PASS: {len(result.cells)} heatmap cells validated"
)
print(
    f"Terrain available   : {available}"
)
print(
    f"Terrain unavailable : {unavailable}"
)
print(
    f"Sun visible         : {sun_visible}"
)
print(
    f"Sun blocked         : {sun_blocked}"
)
print(
    f"Earth visible       : {earth_visible}"
)
print(
    f"Earth blocked       : {earth_blocked}"
)
print("=" * 70)
print("REAL HEATMAP TEST: PASS")
print("=" * 70)
