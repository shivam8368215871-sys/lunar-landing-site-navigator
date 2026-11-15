from __future__ import annotations

from pathlib import Path
import math

import numpy as np

from app.science.lola_terrain import (
    TerrainMetrics,
    TerrainSample,
)


class GlobalLOLATerrain:
    """
    Reader for NASA LRO/LOLA LDEM_64_FLOAT.

    Source metadata:
        11520 rows x 23040 columns
        64 pixels per degree
        Simple cylindrical projection
        Planetocentric latitude
        East-positive longitude
        32-bit little-endian floating-point heights
        Heights in km relative to 1737.4 km

    Coverage:
        -90 to +90 degrees latitude
        0 to 360 degrees east longitude

    This is the global fallback DEM. The existing 40 m
    south-polar reader remains separate and takes priority
    when the two readers are integrated.
    """

    ROWS = 11520
    COLUMNS = 23040

    PIXELS_PER_DEGREE = 64.0

    LINE_PROJECTION_OFFSET = 5759.5
    SAMPLE_PROJECTION_OFFSET = 11519.5

    CENTER_LONGITUDE_DEG = 180.0

    REFERENCE_RADIUS_KM = 1737.4
    PIXEL_SIZE_KM = 0.473802
    RESOLUTION_M = 473.802

    MIN_LATITUDE = -90.0
    MAX_LATITUDE = 90.0

    EXPECTED_SIZE = (
        ROWS * COLUMNS * np.dtype("<f4").itemsize
    )

    def __init__(
        self,
        image_path: str | Path = (
            "data/terrain/lola/global/ldem_64_float.img"
        ),
    ):
        self.image_path = Path(image_path)
        self.label_path = self.image_path.with_suffix(".lbl")
        self._data: np.memmap | None = None

    def load(self) -> None:
        """Validate the PDS product and open it using memory mapping."""

        if self._data is not None:
            return

        if not self.image_path.is_file():
            raise FileNotFoundError(
                f"Global LOLA DEM not found: {self.image_path}"
            )

        if not self.label_path.is_file():
            raise FileNotFoundError(
                f"Global LOLA PDS label not found: {self.label_path}"
            )

        label = self.label_path.read_text(
            encoding="ascii",
            errors="replace",
        )

        required_label_values = (
            'PRODUCT_ID                = "LDEM_64_FLOAT"',
            "LINES                 = 11520",
            "LINE_SAMPLES          = 23040",
            "SAMPLE_TYPE           = PC_REAL",
            "SAMPLE_BITS           = 32",
            'MAP_PROJECTION_TYPE          = "SIMPLE CYLINDRICAL"',
            "MAP_RESOLUTION               = 64 <pix/deg>",
            "CENTER_LATITUDE              = 0 <deg>",
            "CENTER_LONGITUDE             = 180 <deg>",
            "LINE_PROJECTION_OFFSET       = 5759.5 <pix>",
            "SAMPLE_PROJECTION_OFFSET     = 11519.5 <pix>",
        )

        missing = [
            value
            for value in required_label_values
            if value not in label
        ]

        if missing:
            raise ValueError(
                "Global LOLA PDS label does not match the "
                "expected LDEM_64_FLOAT product: "
                + "; ".join(missing)
            )

        actual_size = self.image_path.stat().st_size

        if actual_size != self.EXPECTED_SIZE:
            raise ValueError(
                "Global LOLA DEM size mismatch: "
                f"expected {self.EXPECTED_SIZE} bytes, "
                f"got {actual_size} bytes"
            )

        self._data = np.memmap(
            self.image_path,
            dtype="<f4",
            mode="r",
            shape=(self.ROWS, self.COLUMNS),
        )

        print(
            "Global LOLA DEM loaded:",
            f"{self.ROWS} x {self.COLUMNS}",
            f"({actual_size:,} bytes)",
        )

    def unload(self) -> None:
        """Release the global DEM memory mapping."""

        data = self._data
        self._data = None

        if data is not None:
            data._mmap.close()

    def _require_loaded(self) -> np.memmap:
        if self._data is None:
            raise RuntimeError(
                "Global LOLA terrain is not loaded."
            )

        return self._data

    @staticmethod
    def _validate_coordinates(
        latitude: float,
        longitude: float,
    ) -> tuple[float, float]:
        latitude = float(latitude)
        longitude = float(longitude)

        if not (
            math.isfinite(latitude)
            and math.isfinite(longitude)
        ):
            raise ValueError(
                "Latitude and longitude must be finite numbers."
            )

        if not -90.0 <= latitude <= 90.0:
            raise ValueError(
                f"Latitude {latitude}° is outside "
                "global LOLA coverage [-90°, 90°]."
            )

        # East-positive longitude, wrapped into [0, 360).
        longitude = longitude % 360.0

        return latitude, longitude

    def _project(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[float, float]:
        """
        Project planetocentric coordinates to zero-based
        continuous row and column coordinates.

        The formulas use the offsets and map resolution
        declared by the official PDS label.
        """

        latitude, longitude = self._validate_coordinates(
            latitude,
            longitude,
        )

        longitude_delta = (
            (longitude - self.CENTER_LONGITUDE_DEG + 180.0)
            % 360.0
        ) - 180.0

        row = (
            self.LINE_PROJECTION_OFFSET
            - latitude * self.PIXELS_PER_DEGREE
        )

        column = (
            self.SAMPLE_PROJECTION_OFFSET
            + longitude_delta * self.PIXELS_PER_DEGREE
        )

        return row, column

    def _pixel_indices(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[int, int]:
        row_float, column_float = self._project(
            latitude,
            longitude,
        )

        # Nearest pixel center. Clamp the poles to the first
        # or last row; longitude wraps across the map seam.
        row = math.floor(row_float + 0.5)
        row = min(max(row, 0), self.ROWS - 1)

        column = (
            math.floor(column_float + 0.5)
            % self.COLUMNS
        )

        return row, column

    def display_grid(
        self,
        width: int = 1440,
        height: int = 720,
    ) -> np.ndarray:
        """
        Return a downsampled global elevation grid for visualization.

        The returned array is a copy and does not retain the
        memory-mapped DEM.
        """

        if (
            isinstance(width, bool)
            or isinstance(height, bool)
            or not isinstance(width, int)
            or not isinstance(height, int)
            or width < 2
            or height < 2
        ):
            raise ValueError(
                "Display width and height must be integers >= 2."
            )

        data = self._require_loaded()

        rows = np.linspace(
            0,
            self.ROWS - 1,
            height,
        ).round().astype(np.intp)

        columns = np.linspace(
            0,
            self.COLUMNS - 1,
            width,
        ).round().astype(np.intp)

        return np.asarray(
            data[np.ix_(rows, columns)],
            dtype=np.float32,
        )

    def contains(
        self,
        latitude: float,
        longitude: float,
    ) -> bool:
        """Return whether the coordinate is inside global coverage."""

        try:
            self._validate_coordinates(latitude, longitude)
        except (TypeError, ValueError):
            return False

        return True

    def sample(
        self,
        latitude: float,
        longitude: float,
    ) -> TerrainSample:
        """Read the nearest global DEM pixel."""

        data = self._require_loaded()

        latitude, longitude = self._validate_coordinates(
            latitude,
            longitude,
        )

        row, column = self._pixel_indices(
            latitude,
            longitude,
        )

        height_km = float(data[row, column])

        if not math.isfinite(height_km):
            raise ValueError(
                "Global LOLA DEM contains a non-finite "
                f"height at row {row}, column {column}."
            )

        return TerrainSample(
            latitude=latitude,
            longitude=longitude,
            height_km=height_km,
            radius_km=(
                self.REFERENCE_RADIUS_KM + height_km
            ),
            row=row,
            column=column,
        )

    def terrain_metrics(
        self,
        latitude: float,
        longitude: float,
    ) -> TerrainMetrics:
        """
        Calculate elevation and a local slope estimate.

        North/south spacing follows the global map's
        64-pixel-per-degree scale.

        East/west spacing is latitude-dependent because
        longitude lines converge toward the poles.
        """

        data = self._require_loaded()

        latitude, longitude = self._validate_coordinates(
            latitude,
            longitude,
        )

        row, column = self._pixel_indices(
            latitude,
            longitude,
        )

        center = float(data[row, column])

        if not math.isfinite(center):
            raise ValueError(
                "Global LOLA center elevation is not finite."
            )

        north_row = max(0, row - 1)
        south_row = min(self.ROWS - 1, row + 1)

        north = float(data[north_row, column])
        south = float(data[south_row, column])

        if not (
            math.isfinite(north)
            and math.isfinite(south)
        ):
            raise ValueError(
                "Global LOLA north/south slope samples "
                "contain non-finite values."
            )

        pixel_angle_rad = math.radians(
            1.0 / self.PIXELS_PER_DEGREE
        )

        north_south_distance_km = (
            (south_row - north_row)
            * self.REFERENCE_RADIUS_KM
            * pixel_angle_rad
        )

        if north_south_distance_km <= 0.0:
            raise ValueError(
                "Unable to calculate north/south DEM spacing."
            )

        dz_d_north_south = (
            south - north
        ) / north_south_distance_km

        west_column = (
            column - 1
        ) % self.COLUMNS

        east_column = (
            column + 1
        ) % self.COLUMNS

        west = float(data[row, west_column])
        east = float(data[row, east_column])

        if not (
            math.isfinite(west)
            and math.isfinite(east)
        ):
            raise ValueError(
                "Global LOLA east/west slope samples "
                "contain non-finite values."
            )

        pixel_latitude = (
            self.LINE_PROJECTION_OFFSET - row
        ) / self.PIXELS_PER_DEGREE

        east_west_pixel_distance_km = (
            self.REFERENCE_RADIUS_KM
            * abs(math.cos(math.radians(pixel_latitude)))
            * pixel_angle_rad
        )

        # Longitude has no physical east/west direction at
        # the exact poles. Avoid division by a near-zero value.
        if east_west_pixel_distance_km > 1e-9:
            dz_d_east_west = (
                east - west
            ) / (
                2.0 * east_west_pixel_distance_km
            )
        else:
            dz_d_east_west = 0.0

        gradient = math.hypot(
            dz_d_north_south,
            dz_d_east_west,
        )

        slope_deg = math.degrees(
            math.atan(gradient)
        )

        return TerrainMetrics(
            latitude=latitude,
            longitude=longitude,
            elevation_m=center * 1000.0,
            slope_deg=float(slope_deg),
            row=row,
            column=column,
        )
