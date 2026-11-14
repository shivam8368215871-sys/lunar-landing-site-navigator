from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from app.science.lola_terrain import LOLATerrain


@dataclass(frozen=True)
class HorizonSample:
    azimuth_deg: float
    horizon_elevation_deg: float
    distance_km: float
    latitude: float
    longitude: float


class LOLAHorizonCalculator:
    """
    Terrain horizon calculator using the LOLA South Polar DEM.

    The calculator samples terrain radially from a landing site and
    determines the maximum apparent terrain elevation for each
    azimuth direction.
    """

    def __init__(
        self,
        terrain: LOLATerrain,
        max_distance_km: float = 120.0,
        radial_step_km: float = 1.0,
    ):
        self.terrain = terrain
        self.max_distance_km = max_distance_km
        self.radial_step_km = radial_step_km

    def _inside_raster(
        self,
        latitude: float,
        longitude: float,
    ) -> bool:
        """
        Check whether a geographic coordinate projects onto a
        valid LOLA raster pixel.

        Latitude coverage alone is not sufficient because the
        mathematical -85 degree boundary projects slightly beyond
        the final raster pixel.
        """

        if not (
            self.terrain.MIN_LATITUDE
            <= latitude
            <= self.terrain.MAX_LATITUDE
        ):
            return False

        row_float, column_float = self.terrain._project(
            latitude,
            longitude,
        )

        return (
            0.0 <= row_float < self.terrain.ROWS
            and 0.0 <= column_float < self.terrain.COLUMNS
        )

    @staticmethod
    def _destination(
        latitude_deg: float,
        longitude_deg: float,
        distance_km: float,
        azimuth_deg: float,
        radius_km: float = 1737.4,
    ) -> tuple[float, float]:
        """
        Approximate destination on a spherical Moon.

        This is used only for selecting DEM samples.
        """

        lat1 = math.radians(latitude_deg)
        lon1 = math.radians(longitude_deg)
        az = math.radians(azimuth_deg)

        angular_distance = distance_km / radius_km

        sin_lat2 = (
            math.sin(lat1) * math.cos(angular_distance)
            + math.cos(lat1)
            * math.sin(angular_distance)
            * math.cos(az)
        )

        lat2 = math.asin(
            max(-1.0, min(1.0, sin_lat2))
        )

        lon2 = lon1 + math.atan2(
            math.sin(az)
            * math.sin(angular_distance)
            * math.cos(lat1),
            math.cos(angular_distance)
            - math.sin(lat1) * math.sin(lat2),
        )

        lon2_deg = math.degrees(lon2)

        lon2_deg = (
            (lon2_deg + 180.0) % 360.0
        ) - 180.0

        return math.degrees(lat2), lon2_deg

    @staticmethod
    def _surface_point(
        latitude_deg: float,
        longitude_deg: float,
        radius_km: float,
    ) -> np.ndarray:
        lat = math.radians(latitude_deg)
        lon = math.radians(longitude_deg)

        cos_lat = math.cos(lat)

        return np.array(
            [
                radius_km * cos_lat * math.cos(lon),
                radius_km * cos_lat * math.sin(lon),
                radius_km * math.sin(lat),
            ],
            dtype=float,
        )

    def terrain_horizon(
        self,
        latitude: float,
        longitude: float,
        azimuth_deg: float,
    ) -> HorizonSample:
        """
        Determine the highest terrain elevation along one azimuth.
        """

        observer = self.terrain.sample(
            latitude,
            longitude,
        )

        observer_position = self._surface_point(
            latitude,
            longitude,
            observer.radius_km,
        )

        best_elevation = -90.0
        best_distance = 0.0
        best_latitude = latitude
        best_longitude = longitude

        distance = self.radial_step_km

        while distance <= self.max_distance_km:
            sample_lat, sample_lon = self._destination(
                latitude,
                longitude,
                distance,
                azimuth_deg,
            )

            if not self._inside_raster(
                sample_lat,
                sample_lon,
            ):
                distance += self.radial_step_km
                continue

            sample = self.terrain.sample(
                sample_lat,
                sample_lon,
            )

            terrain_position = self._surface_point(
                sample_lat,
                sample_lon,
                sample.radius_km,
            )

            vector = terrain_position - observer_position
            horizontal_distance = np.linalg.norm(vector)

            if horizontal_distance > 0:
                observer_up = (
                    observer_position
                    / np.linalg.norm(observer_position)
                )

                vertical_component = float(
                    np.dot(vector, observer_up)
                )

                horizontal_component = math.sqrt(
                    max(
                        0.0,
                        horizontal_distance**2
                        - vertical_component**2,
                    )
                )

                elevation_deg = math.degrees(
                    math.atan2(
                        vertical_component,
                        horizontal_component,
                    )
                )

                if elevation_deg > best_elevation:
                    best_elevation = elevation_deg
                    best_distance = distance
                    best_latitude = sample_lat
                    best_longitude = sample_lon

            distance += self.radial_step_km

        return HorizonSample(
            azimuth_deg=float(azimuth_deg),
            horizon_elevation_deg=float(best_elevation),
            distance_km=float(best_distance),
            latitude=float(best_latitude),
            longitude=float(best_longitude),
        )

    def horizon_profile(
        self,
        latitude: float,
        longitude: float,
        azimuth_step_deg: float = 5.0,
    ) -> list[HorizonSample]:
        """
        Calculate a complete 360-degree terrain horizon profile.
        """

        samples = []

        azimuth = 0.0

        while azimuth < 360.0:
            samples.append(
                self.terrain_horizon(
                    latitude,
                    longitude,
                    azimuth,
                )
            )

            azimuth += azimuth_step_deg

        return samples
