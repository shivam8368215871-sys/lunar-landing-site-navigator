import math

import numpy as np
import spiceypy as spice


class LunarHorizonCalculator:
    """
    Converts a target position from a Moon-fixed frame into
    local elevation and azimuth at a lunar surface site.
    """

    def site_position(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> np.ndarray:
        """
        Convert lunar latitude/longitude into a Moon-centered
        Cartesian position using a spherical Moon model.

        Angles are supplied in degrees.
        """

        lat = math.radians(latitude)
        lon = math.radians(longitude)

        cos_lat = math.cos(lat)

        return np.array([
            radius_km * cos_lat * math.cos(lon),
            radius_km * cos_lat * math.sin(lon),
            radius_km * math.sin(lat),
        ])

    def site_basis(
        self,
        latitude: float,
        longitude: float,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Build local Up, North and East unit vectors.
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
        target_position: tuple[float, float, float],
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> tuple[float, float]:
        """
        Calculate local elevation and azimuth of a target.

        target_position must be expressed in the same Moon-fixed
        coordinate frame used for the site position.

        Returns:
            elevation, azimuth in degrees.
        """

        target = np.asarray(target_position, dtype=float)

        site = self.site_position(
            latitude,
            longitude,
            radius_km,
        )

        direction = target - site

        distance = np.linalg.norm(direction)

        if distance == 0:
            raise ValueError(
                "Target position cannot be identical to site position."
            )

        direction /= distance

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
