from datetime import datetime

import numpy as np
import spiceypy as spice

from app.science.lola_horizon import LOLAHorizonCalculator
from app.science.lola_terrain import LOLATerrain
from app.science.lunar_horizon import LunarHorizonCalculator
from app.science.spice_calculator import SpiceCalculator


class LunarObserver:
    """
    Performs real lunar surface observations using NASA SPICE.

    The target position is calculated relative to the Moon,
    transformed into the Moon-fixed IAU_MOON frame, and then
    converted into local lunar elevation and azimuth.

    When the selected site falls inside the available LOLA
    South Polar DEM coverage, the celestial elevation is also
    compared against the local terrain horizon.
    """

    MOON_RADIUS_KM = 1737.4

    LOLA_MIN_LATITUDE = -90.0
    LOLA_MAX_LATITUDE = -85.0

    def __init__(self, kernel_directory: str = "data/kernels"):
        self.spice = SpiceCalculator()

        # Existing spherical/geometric horizon calculator.
        self.horizon = LunarHorizonCalculator()

        # Real NASA LRO/LOLA terrain.
        self.terrain = LOLATerrain()

        self.lola_horizon = LOLAHorizonCalculator(
            terrain=self.terrain,
            max_distance_km=120.0,
            radial_step_km=1.0,
        )

        self.kernel_directory = kernel_directory

    def load(self) -> None:
        """Load the required SPICE kernels and LOLA terrain."""

        self.spice.load_kernels(self.kernel_directory)
        self.terrain.load()

    def unload(self) -> None:
        """Unload SPICE kernels and release LOLA terrain."""

        self.terrain.unload()
        self.spice.unload_kernels()

    @classmethod
    def lola_coverage_contains(
        cls,
        latitude: float,
    ) -> bool:
        """Return whether a latitude is covered by the loaded LOLA DEM."""

        return (
            cls.LOLA_MIN_LATITUDE
            <= latitude
            <= cls.LOLA_MAX_LATITUDE
        )

    def observe(
        self,
        target: str,
        latitude: float,
        longitude: float,
        analysis_time: datetime,
    ) -> dict:
        """
        Calculate the local observation of a target.

        The returned geometric elevation/azimuth always come from
        the SPICE + spherical lunar geometry calculation.

        Terrain-aware fields are added when the site lies inside
        the available LOLA South Polar DEM.
        """

        et = self.spice.utc_to_et(analysis_time)

        # ---------------------------------------------------------
        # 1. Real SPICE target position relative to the Moon.
        # ---------------------------------------------------------
        target_position_j2000, _ = spice.spkpos(
            target,
            et,
            "J2000",
            "NONE",
            "MOON",
        )

        # ---------------------------------------------------------
        # 2. Transform target position into Moon-fixed coordinates.
        # ---------------------------------------------------------
        rotation = spice.pxform(
            "J2000",
            "IAU_MOON",
            et,
        )

        target_position_moon_fixed = (
            rotation @ target_position_j2000
        )

        distance_km = float(
            np.linalg.norm(target_position_moon_fixed)
        )

        # ---------------------------------------------------------
        # 3. Existing geometric spherical-horizon calculation.
        # ---------------------------------------------------------
        elevation, azimuth = (
            self.horizon.elevation_azimuth(
                target_position=target_position_moon_fixed,
                latitude=latitude,
                longitude=longitude,
                radius_km=self.MOON_RADIUS_KM,
            )
        )

        geometric_visible = elevation > 0.0

        # ---------------------------------------------------------
        # 4. Terrain-aware calculation.
        # ---------------------------------------------------------
        terrain_horizon_elevation = None
        terrain_visible = None
        terrain_status = None
        terrain_horizon_distance_km = None

        if self.lola_coverage_contains(latitude):
            terrain_horizon = (
                self.lola_horizon.terrain_horizon(
                    latitude=latitude,
                    longitude=longitude,
                    azimuth_deg=azimuth,
                )
            )

            terrain_horizon_elevation = (
                terrain_horizon.horizon_elevation_deg
            )

            terrain_horizon_distance_km = (
                terrain_horizon.distance_km
            )

            # distance_km == 0 means that no usable DEM sample
            # was found along this azimuth.
            if terrain_horizon.distance_km > 0.0:
                terrain_visible = (
                    elevation
                    > terrain_horizon_elevation
                )

                if terrain_visible:
                    terrain_status = "Terrain Clear"
                else:
                    terrain_status = "Terrain Blocked"
            else:
                terrain_status = (
                    "Terrain Unavailable Along Azimuth"
                )

        else:
            terrain_status = (
                "Outside LOLA DEM Coverage"
            )

        return {
            "target": target,
            "distance_km": distance_km,
            "elevation": elevation,
            "azimuth": azimuth,
            "visible": geometric_visible,

            # Terrain-aware information.
            "terrain_horizon_elevation":
                terrain_horizon_elevation,
            "terrain_visible":
                terrain_visible,
            "terrain_status":
                terrain_status,
            "terrain_horizon_distance_km":
                terrain_horizon_distance_km,
        }
