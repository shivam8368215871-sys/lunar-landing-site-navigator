from datetime import datetime, timezone

import spiceypy as spice


class SpiceCalculator:
    """
    Low-level wrapper around NASA SPICE calculations.

    This class is responsible only for obtaining astronomical
    positions from the loaded SPICE kernels.
    """

    def __init__(self):
        self.loaded = False

    def load_kernels(self, kernel_directory: str = "data/kernels") -> None:
        """
        Load all supported SPICE kernels from the given directory.
        """

        from app.science.spice_manager import SpiceManager

        self.manager = SpiceManager(kernel_directory)
        self.manager.load_kernels()
        self.loaded = True

    def unload_kernels(self) -> None:
        """Unload all SPICE kernels."""
        if self.loaded:
            self.manager.unload_kernels()
            self.loaded = False

    def utc_to_et(self, analysis_time: datetime) -> float:
        """
        Convert a UTC datetime to SPICE ephemeris time.
        """

        if analysis_time.tzinfo is None:
            analysis_time = analysis_time.replace(tzinfo=timezone.utc)

        utc_string = analysis_time.strftime("%Y-%m-%dT%H:%M:%S")
        return spice.str2et(utc_string)

    def get_position(
        self,
        target: str,
        observer: str,
        analysis_time: datetime,
        frame: str = "J2000",
    ) -> tuple[float, float, float]:
        """
        Get the position of a target relative to an observer.

        Returns:
            (x, y, z) in kilometers.
        """

        if not self.loaded:
            raise RuntimeError("SPICE kernels are not loaded.")

        et = self.utc_to_et(analysis_time)

        position, _ = spice.spkpos(
            target,
            et,
            frame,
            "NONE",
            observer,
        )

        return tuple(float(value) for value in position)
