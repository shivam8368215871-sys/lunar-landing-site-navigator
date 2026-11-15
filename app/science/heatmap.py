from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import math

from app.core.models import Site
from app.science.engine import LunarAnalysisEngine


@dataclass(frozen=True)
class HeatmapCell:
    """One sampled position in the LOLA south-polar raster."""

    row: float
    column: float
    latitude: float
    longitude: float

    terrain_available: bool

    sun_visible: bool | None
    earth_visible: bool | None

    sun_status: str
    earth_status: str


@dataclass(frozen=True)
class HeatmapResult:
    """Geographic Sun/Earth visibility grid for one UTC timestamp."""

    analysis_time: datetime
    grid_size: int
    cells: tuple[HeatmapCell, ...]

    @property
    def available_cells(self) -> int:
        return sum(cell.terrain_available for cell in self.cells)

    @property
    def unavailable_cells(self) -> int:
        return len(self.cells) - self.available_cells


def pixel_to_coordinate(
    row: float,
    column: float,
) -> tuple[float, float]:
    """
    Convert LOLA south-polar raster coordinates to lunar
    planetocentric latitude and longitude.

    Projection parameters are taken from the LOLA PDS label
    and the existing LOLATerrain implementation.
    """

    from app.science.lola_terrain import LOLATerrain

    radius = LOLATerrain.REFERENCE_RADIUS_KM
    pixel_size = LOLATerrain.PIXEL_SIZE_KM
    center_row = LOLATerrain.LINE_PROJECTION_OFFSET
    center_column = LOLATerrain.SAMPLE_PROJECTION_OFFSET

    x = (column - center_column) * pixel_size
    y = (row - center_row) * pixel_size

    rho = math.hypot(x, y)

    latitude_rad = 2.0 * (
        math.atan(rho / (2.0 * radius))
        - math.pi / 4.0
    )

    latitude = math.degrees(latitude_rad)
    longitude = math.degrees(math.atan2(x, -y))

    return latitude, longitude


def calculate_visibility_heatmap(
    engine: LunarAnalysisEngine,
    analysis_time: datetime,
    grid_size: int = 32,
) -> HeatmapResult:
    """
    Calculate real terrain-aware Sun/Earth visibility over
    a regular grid covering the LOLA south-polar raster.

    Every valid cell uses LunarAnalysisEngine.analyze(), which
    performs the existing NASA SPICE and LOLA horizon calculations.

    Invalid or unavailable DEM positions are retained in the
    result with None visibility values. No values are interpolated.
    """

    if isinstance(grid_size, bool) or not isinstance(grid_size, int):
        raise TypeError("grid_size must be an integer.")

    if not 2 <= grid_size <= 128:
        raise ValueError("grid_size must be between 2 and 128.")

    terrain = engine.observer.terrain

    cells = []

    row_step = terrain.ROWS / grid_size
    column_step = terrain.COLUMNS / grid_size

    for row_index in range(grid_size):
        for column_index in range(grid_size):

            row = (row_index + 0.5) * row_step
            column = (column_index + 0.5) * column_step

            latitude, longitude = pixel_to_coordinate(
                row,
                column,
            )

            # First validate the actual DEM sample. This checks
            # geographic coverage, raster bounds, and finite data.
            try:
                terrain.sample(
                    latitude,
                    longitude,
                )

            except ValueError:
                cells.append(
                    HeatmapCell(
                        row=row,
                        column=column,
                        latitude=latitude,
                        longitude=longitude,
                        terrain_available=False,
                        sun_visible=None,
                        earth_visible=None,
                        sun_status="Terrain Unavailable",
                        earth_status="Terrain Unavailable",
                    )
                )
                continue

            site = Site(
                name=(
                    f"Heatmap {row_index + 1}-"
                    f"{column_index + 1}"
                ),
                latitude=latitude,
                longitude=longitude,
            )

            # Use the established science pipeline without
            # replacing or approximating its calculations.
            result = engine.analyze(
                site,
                analysis_time,
            )

            cells.append(
                HeatmapCell(
                    row=row,
                    column=column,
                    latitude=latitude,
                    longitude=longitude,
                    terrain_available=True,
                    sun_visible=result.sun.terrain_visible,
                    earth_visible=result.earth.terrain_visible,
                    sun_status=(
                        result.sun.terrain_status
                        or "Terrain Result Unavailable"
                    ),
                    earth_status=(
                        result.earth.terrain_status
                        or "Terrain Result Unavailable"
                    ),
                )
            )

    return HeatmapResult(
        analysis_time=analysis_time,
        grid_size=grid_size,
        cells=tuple(cells),
    )
