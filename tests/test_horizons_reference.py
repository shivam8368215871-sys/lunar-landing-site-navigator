import json
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.data.sites import LANDING_SITES
from app.science.engine import LunarAnalysisEngine


HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"

ANALYSIS_TIME = datetime(
    2026,
    1,
    1,
    0,
    0,
    0,
)

AZIMUTH_TOLERANCE = 0.01
ELEVATION_TOLERANCE = 0.01

SITE_HEIGHTS_KM = {
    "Shackleton Crater": 0.640898,
    "Cabeus Crater": 5.777316,
    "Malapert Massif": 4.829088,
}


def query_horizons(target, site):
    params = {
        "format": "json",
        "COMMAND": f"'{target}'",
        "OBJ_DATA": "NO",
        "MAKE_EPHEM": "YES",
        "EPHEM_TYPE": "OBSERVER",
        "CENTER": "'coord@301'",
        "COORD_TYPE": "GEODETIC",
        "SITE_COORD": (
            f"'{site.longitude},{site.latitude},"
            f"{SITE_HEIGHTS_KM[site.name]:.6f}'"
        ),
        "START_TIME": "'2026-01-01 00:00'",
        "STOP_TIME": "'2026-01-01 00:01'",
        "STEP_SIZE": "'1 m'",
        "QUANTITIES": "'4'",
        "TIME_TYPE": "UT",
        "REF_SYSTEM": "ICRF",
    }

    url = (
        HORIZONS_URL
        + "?"
        + urllib.parse.urlencode(params)
    )

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Lunar-Landing-Site-Navigator/1.0 "
                "(NASA Space Apps validation)"
            )
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=20,
    ) as response:
        data = json.load(response)

    result_text = data["result"]

    data_start = (
        result_text.index("$$SOE")
        + len("$$SOE")
    )

    data_end = result_text.index("$$EOE")

    data_line = next(
        line.strip()
        for line in result_text[
            data_start:data_end
        ].splitlines()
        if line.strip()
    )

    parts = data_line.split()

    return {
        "azimuth": float(parts[3]),
        "elevation": float(parts[4]),
    }


def main():
    print()
    print("=" * 72)
    print("LUNAR LANDING SITE NAVIGATOR")
    print("JPL HORIZONS / SPICE REFERENCE VALIDATION")
    print("=" * 72)

    print()
    print(f"UTC: {ANALYSIS_TIME.isoformat()}")
    print(
        f"Azimuth tolerance: "
        f"±{AZIMUTH_TOLERANCE:.3f}°"
    )
    print(
        f"Elevation tolerance: "
        f"±{ELEVATION_TOLERANCE:.3f}°"
    )

    engine = LunarAnalysisEngine()
    engine.load()

    all_passed = True

    try:
        for site in LANDING_SITES.values():
            result = engine.analyze(
                site,
                ANALYSIS_TIME,
            )

            print()
            print("=" * 72)
            print(site.name)
            print("=" * 72)

            for target, spice_result in (
                ("Sun", result.sun),
                ("Earth", result.earth),
            ):
                horizons_target = (
                    "SUN"
                    if target == "Sun"
                    else "399"
                )

                reference = query_horizons(
                    horizons_target,
                    site,
                )

                azimuth_difference = abs(
                    spice_result.azimuth
                    - reference["azimuth"]
                )

                elevation_difference = abs(
                    spice_result.elevation
                    - reference["elevation"]
                )

                azimuth_pass = (
                    azimuth_difference
                    <= AZIMUTH_TOLERANCE
                )

                elevation_pass = (
                    elevation_difference
                    <= ELEVATION_TOLERANCE
                )

                all_passed &= (
                    azimuth_pass
                    and elevation_pass
                )

                print()
                print(target)

                print(
                    f"  Azimuth   "
                    f"SPICE={spice_result.azimuth:.6f}° "
                    f"Horizons={reference['azimuth']:.6f}° "
                    f"diff={azimuth_difference:.6f}° "
                    f"[{'PASS' if azimuth_pass else 'FAIL'}]"
                )

                print(
                    f"  Elevation "
                    f"SPICE={spice_result.elevation:.6f}° "
                    f"Horizons={reference['elevation']:.6f}° "
                    f"diff={elevation_difference:.6f}° "
                    f"[{'PASS' if elevation_pass else 'FAIL'}]"
                )

    finally:
        engine.unload()

    print()
    print("=" * 72)

    if all_passed:
        print(
            "PASS: All three sites agree with JPL Horizons"
        )
        print("PASS: Sun reference validation")
        print("PASS: Earth reference validation")
        print(
            "PASS: Azimuth tolerance = ±0.010°"
        )
        print(
            "PASS: Elevation tolerance = ±0.010°"
        )
        print(
            "JPL HORIZONS REFERENCE VALIDATION: PASS"
        )
        print("=" * 72)
        return 0

    print(
        "FAIL: One or more JPL Horizons comparisons "
        "exceeded tolerance"
    )
    print(
        "JPL HORIZONS REFERENCE VALIDATION: FAIL"
    )
    print("=" * 72)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
