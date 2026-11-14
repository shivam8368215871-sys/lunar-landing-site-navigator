from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np


@dataclass(frozen=True)
class TerrainSample:
    latitude: float
    longitude: float
    height_km: float
    radius_km: float
    row: int
    column: int


class LOLATerrain:
    """
    Reader for the NASA LRO/LOLA LDEM_85S_40M_FLOAT product.

    Product:
        LDEM_85S_40M_FLOAT.IMG

    Coverage:
        -90 deg <= latitude <= -85 deg

    Projection:
        South polar stereographic

    Resolution:
        40 m/pixel

    The binary values are terrain height in km relative to
    the reference radius of 1737.4 km.
    """

    ROWS = 7584
    COLUMNS = 7584
    PIXEL_SIZE_KM = 0.040
    REFERENCE_RADIUS_KM = 1737.4

    CENTER_LATITUDE_DEG = -90.0
    CENTER_LONGITUDE_DEG = 0.0

    # From the PDS label:
    LINE_PROJECTION_OFFSET = 3791.5
    SAMPLE_PROJECTION_OFFSET = 3791.5

    MIN_LATITUDE = -90.0
    MAX_LATITUDE = -85.0

    def __init__(
        self,
        image_path: str | Path = (
            "data/terrain/lola/ldem_85s_40m_float.img"
        ),
    ):
        self.image_path = Path(image_path)
        self._data: np.memmap | None = None

    def load(self) -> None:
        """Open the LOLA binary using memory mapping."""

        if not self.image_path.exists():
            raise FileNotFoundError(
                f"LOLA DEM not found: {self.image_path}"
            )

        expected_size = (
            self.ROWS
            * self.COLUMNS
            * np.dtype("<f4").itemsize
        )

        actual_size = self.image_path.stat().st_size

        if actual_size != expected_size:
            raise ValueError(
                "LOLA DEM size mismatch: "
                f"expected {expected_size} bytes, "
                f"got {actual_size} bytes"
            )

        self._data = np.memmap(
            self.image_path,
            dtype="<f4",
            mode="r",
            shape=(self.ROWS, self.COLUMNS),
        )

    def unload(self) -> None:
        """Release the memory-mapped DEM."""

        self._data = None

    def _require_loaded(self) -> np.memmap:
        if self._data is None:
            raise RuntimeError("LOLA terrain is not loaded.")

        return self._data

    @staticmethod
    def _normalize_longitude(longitude: float) -> float:
        """
        Normalize longitude to [-180, 180).
        """

        return ((longitude + 180.0) % 360.0) - 180.0

    def _project(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[float, float]:
        """
        Convert lunar planetocentric latitude/longitude to
        South Polar stereographic image coordinates.

        Returns:
            row_float, column_float
        """

        if not (
            self.MIN_LATITUDE
            <= latitude
            <= self.MAX_LATITUDE
        ):
            raise ValueError(
                f"Latitude {latitude}° is outside the LOLA "
                f"DEM coverage [{self.MIN_LATITUDE}°, "
                f"{self.MAX_LATITUDE}°]."
            )

        longitude = self._normalize_longitude(longitude)

        # South-polar stereographic distance from the pole.
        #
        # For a sphere:
        #
        #   rho = 2R * tan(pi/4 + phi/2)
        #
        # where phi is planetocentric latitude.
        #
        # At -90°: rho = 0
        # At -85°: rho ≈ 151.7 km
        phi = math.radians(latitude)
        lam = math.radians(longitude)

        rho_km = (
            2.0
            * self.REFERENCE_RADIUS_KM
            * math.tan(math.pi / 4.0 + phi / 2.0)
        )

        # The PDS label gives a 0° projection rotation.
        #
        # Image coordinates:
        #   sample -> x
        #   line   -> y
        #
        # South-polar maps increase outward from the pole.
        x_km = rho_km * math.sin(lam)
        y_km = -rho_km * math.cos(lam)

        column = (
            self.SAMPLE_PROJECTION_OFFSET
            + x_km / self.PIXEL_SIZE_KM
        )

        row = (
            self.LINE_PROJECTION_OFFSET
            + y_km / self.PIXEL_SIZE_KM
        )

        return row, column

    def sample(
        self,
        latitude: float,
        longitude: float,
    ) -> TerrainSample:
        """
        Sample the LOLA terrain at the nearest DEM pixel.
        """

        data = self._require_loaded()

        row_float, column_float = self._project(
            latitude,
            longitude,
        )

        row = int(round(row_float))
        column = int(round(column_float))

        if not (
            0 <= row < self.ROWS
            and 0 <= column < self.COLUMNS
        ):
            raise ValueError(
                "Projected coordinate falls outside the "
                "LOLA raster."
            )

        height_km = float(data[row, column])

        if not math.isfinite(height_km):
            raise ValueError(
                f"LOLA terrain sample is not finite at "
                f"({latitude}, {longitude})."
            )

        radius_km = (
            self.REFERENCE_RADIUS_KM
            + height_km
        )

        return TerrainSample(
            latitude=float(latitude),
            longitude=float(longitude),
            height_km=height_km,
            radius_km=radius_km,
            row=row,
            column=column,
        )
