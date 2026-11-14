import math

import numpy as np


class LunarCoordinateCalculator:
    """
    Converts Moon-fixed Cartesian vectors into local
    lunar horizon coordinates.
    """

    def site_basis(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Build local Up, North and East unit vectors for
        a spherical Moon.

        Angles are supplied in degrees.
        """

        lat = math.radians(latitude)
        lon = math.radians(longitude)

        cos_lat = math.cos(lat)
        sin_lat = math.sin(lat)
        cos_lon = math.cos(lon)
        sin_lon = math.sin(lon)

        up = np.array([
            cos_lat * cos_lon,
            cos_lat * sin_lon,
            sin_lat,
        ])

        north = np.array([
            -sin_lat * cos_lon,
            -sin_lat * sin_lon,
            cos_lat,
        ])

        east = np.array([
            -sin_lon,
            cos_lon,
            0.0,
        ])

        return up, north, east

    def elevation_azimuth(
        self,
        vector: tuple[float, float, float],
        latitude: float,
        longitude: float,
    ) -> tuple[float, float]:
        """
        Convert a Moon-centered direction vector into
        local elevation and azimuth.

        Returns:
            elevation, azimuth in degrees.

        Azimuth:
            0°   = North
            90°  = East
            180° = South
            270° = West
        """

        direction = np.asarray(vector, dtype=float)

        magnitude = np.linalg.norm(direction)

        if magnitude == 0:
            raise ValueError("Direction vector cannot be zero.")

        direction /= magnitude

        up, north, east = self.site_basis(
            latitude,
            longitude,
        )

        up_component = np.dot(direction, up)
        north_component = np.dot(direction, north)
        east_component = np.dot(direction, east)

        elevation = math.degrees(
            math.asin(np.clip(up_component, -1.0, 1.0))
        )

        azimuth = math.degrees(
            math.atan2(east_component, north_component)
        )

        azimuth %= 360.0

        return elevation, azimuth
