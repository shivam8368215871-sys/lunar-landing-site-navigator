from pathlib import Path

import spiceypy as spice


class SpiceManager:
    """
    Handles loading and unloading NASA SPICE kernels.
    """

    KERNEL_EXTENSIONS = {
        ".bsp",  # SPK ephemeris
        ".bpc",  # binary planetary constants
        ".tpc",  # text planetary constants
        ".tls",  # leapseconds
        ".tf",   # frame kernel
    }

    def __init__(self, kernel_directory: str = "data/kernels"):
        self.kernel_directory = Path(kernel_directory)
        self.loaded = False

    def load_kernels(self) -> None:
        """
        Load supported SPICE kernel files from the kernel directory.
        """

        if not self.kernel_directory.exists():
            raise FileNotFoundError(
                f"SPICE kernel directory not found: "
                f"{self.kernel_directory}"
            )

        kernel_files = sorted(
            path
            for path in self.kernel_directory.iterdir()
            if path.is_file()
            and path.suffix.lower() in self.KERNEL_EXTENSIONS
        )

        if not kernel_files:
            raise FileNotFoundError(
                f"No SPICE kernels found in {self.kernel_directory}"
            )

        for kernel in kernel_files:
            spice.furnsh(str(kernel))

        self.loaded = True

    def unload_kernels(self) -> None:
        """Unload all currently loaded SPICE kernels."""
        spice.kclear()
        self.loaded = False