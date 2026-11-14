import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import math
from datetime import datetime, timedelta
from pathlib import Path

import spiceypy as spice

from app.core.models import Site
from app.data.sites import LANDING_SITES
from app.science.engine import LunarAnalysisEngine


PASS = 0
FAIL = 0


def check(name, condition, detail=""):
    global PASS, FAIL

    if condition:
        PASS += 1
        print(f"[PASS] {name}")
        if detail:
            print(f"       {detail}")
    else:
        FAIL += 1
        print(f"[FAIL] {name}")
        if detail:
            print(f"       {detail}")


def finite(value):
    return isinstance(value, (int, float)) and math.isfinite(value)


def main():
    print()
    print("=" * 70)
    print("LUNAR LANDING SITE NAVIGATOR")
    print("REAL SCIENCE / SPICE INTEGRITY TEST")
    print("=" * 70)

    root = Path(__file__).resolve().parents[1]
    kernel_dir = root / "data" / "kernels"

    print()
    print(f"Project: {root}")
    print(f"Kernels: {kernel_dir}")

    # --------------------------------------------------
    # 1. KERNEL EXISTENCE
    # --------------------------------------------------

    required_kernels = [
        "de440s.bsp",
        "moon_pa_de440_200625.bpc",
        "pck00011.tpc",
        "naif0012.tls",
    ]

    print()
    print("1. KERNEL FILE CHECK")
    print("-" * 70)

    for filename in required_kernels:
        path = kernel_dir / filename

        check(
            f"Kernel exists: {filename}",
            path.exists() and path.stat().st_size > 0,
            f"size={path.stat().st_size if path.exists() else 0} bytes",
        )

    # --------------------------------------------------
    # 2. DIRECT SPICE CHECK
    # --------------------------------------------------

    print()
    print("2. DIRECT SPICE CHECK")
    print("-" * 70)

    try:
        spice.kclear()

        for filename in required_kernels:
            spice.furnsh(str(kernel_dir / filename))

        check(
            "SPICE kernels load",
            spice.ktotal("ALL") >= len(required_kernels),
            f"loaded kernels={spice.ktotal('ALL')}",
        )

    except Exception as exc:
        check(
            "SPICE kernels load",
            False,
            repr(exc),
        )
        print()
        print("Cannot continue scientific tests.")
        return 1

    # --------------------------------------------------
    # 3. FRAME CHECK
    # --------------------------------------------------

    print()
    print("3. SPICE FRAME CHECK")
    print("-" * 70)

    try:
        j2000 = spice.namfrm("J2000")
        moon_frame = spice.namfrm("IAU_MOON")

        check(
            "J2000 frame available",
            j2000 != 0,
            f"J2000={j2000}",
        )

        check(
            "IAU_MOON frame available",
            moon_frame != 0,
            f"IAU_MOON={moon_frame}",
        )

    except Exception as exc:
        check(
            "SPICE frame lookup",
            False,
            repr(exc),
        )

    # --------------------------------------------------
    # 4. DIRECT REAL SUN POSITION
    # --------------------------------------------------

    print()
    print("4. DIRECT REAL SUN POSITION")
    print("-" * 70)

    t1 = datetime(2026, 1, 1, 0, 0, 0)
    t2 = datetime(2026, 1, 2, 0, 0, 0)

    et1 = spice.str2et(
        t1.strftime("%Y-%m-%dT%H:%M:%S")
    )

    et2 = spice.str2et(
        t2.strftime("%Y-%m-%dT%H:%M:%S")
    )

    sun1, _ = spice.spkpos(
        "SUN",
        et1,
        "IAU_MOON",
        "LT+S",
        "MOON",
    )

    sun2, _ = spice.spkpos(
        "SUN",
        et2,
        "IAU_MOON",
        "LT+S",
        "MOON",
    )

    sun_changed = any(
        abs(float(a) - float(b)) > 1e-10
        for a, b in zip(sun1, sun2)
    )

    check(
        "SUN position is finite",
        all(finite(float(x)) for x in sun1),
        f"SUN @ t1 = {sun1}",
    )

    check(
        "SUN position changes with time",
        sun_changed,
        f"t1={sun1}, t2={sun2}",
    )

    # --------------------------------------------------
    # 5. DIRECT REAL EARTH POSITION
    # --------------------------------------------------

    print()
    print("5. DIRECT REAL EARTH POSITION")
    print("-" * 70)

    earth1, _ = spice.spkpos(
        "EARTH",
        et1,
        "IAU_MOON",
        "LT+S",
        "MOON",
    )

    earth2, _ = spice.spkpos(
        "EARTH",
        et2,
        "IAU_MOON",
        "LT+S",
        "MOON",
    )

    earth_changed = any(
        abs(float(a) - float(b)) > 1e-10
        for a, b in zip(earth1, earth2)
    )

    check(
        "EARTH position is finite",
        all(finite(float(x)) for x in earth1),
        f"EARTH @ t1 = {earth1}",
    )

    check(
        "EARTH position changes with time",
        earth_changed,
        f"t1={earth1}, t2={earth2}",
    )

    # --------------------------------------------------
    # 6. ENGINE LOAD
    # --------------------------------------------------

    print()
    print("6. LUNAR ANALYSIS ENGINE")
    print("-" * 70)

    engine = LunarAnalysisEngine(
        kernel_directory=str(kernel_dir)
    )

    try:
        engine.load()

        check(
            "LunarAnalysisEngine loads",
            True,
        )

        # ------------------------------------------------
        # 7. REAL SITE ANALYSIS
        # ------------------------------------------------

        print()
        print("7. REAL SITE ANALYSIS")
        print("-" * 70)

        results = {}

        for name, site in LANDING_SITES.items():

            result = engine.analyze(
                site,
                t1,
            )

            results[name] = result

            print()
            print(f"Site: {name}")
            print(
                f"  Latitude : {site.latitude:.6f}°"
            )
            print(
                f"  Longitude: {site.longitude:.6f}°"
            )

            print(
                f"  Sun      : "
                f"elev={result.sun.elevation:.6f}° "
                f"az={result.sun.azimuth:.6f}° "
                f"visible={result.sun.visible}"
            )

            print(
                f"  Earth    : "
                f"elev={result.earth.elevation:.6f}° "
                f"az={result.earth.azimuth:.6f}° "
                f"visible={result.earth.visible}"
            )

            check(
                f"{name}: Sun elevation finite",
                finite(result.sun.elevation),
            )

            check(
                f"{name}: Sun azimuth finite",
                finite(result.sun.azimuth),
            )

            check(
                f"{name}: Earth elevation finite",
                finite(result.earth.elevation),
            )

            check(
                f"{name}: Earth azimuth finite",
                finite(result.earth.azimuth),
            )

            check(
                f"{name}: Sun visibility consistent",
                result.sun.visible
                == (result.sun.elevation >= 0),
                (
                    f"elevation={result.sun.elevation:.6f}, "
                    f"visible={result.sun.visible}"
                ),
            )

            check(
                f"{name}: Earth visibility consistent",
                result.earth.visible
                == (result.earth.elevation >= 0),
                (
                    f"elevation={result.earth.elevation:.6f}, "
                    f"visible={result.earth.visible}"
                ),
            )

            check(
                f"{name}: Result time preserved",
                result.time == t1,
            )

            check(
                f"{name}: Site preserved",
                result.site.latitude == site.latitude
                and result.site.longitude == site.longitude,
            )

        # ------------------------------------------------
        # 8. LOLA TERRAIN INTEGRITY TEST
        # ------------------------------------------------

        print()
        print("8. LOLA TERRAIN INTEGRITY TEST")
        print("-" * 70)

        lola_image = (
            root
            / "data"
            / "terrain"
            / "lola"
            / "ldem_85s_40m_float.img"
        )

        expected_lola_size = (
            7584
            * 7584
            * 4
        )

        actual_lola_size = (
            lola_image.stat().st_size
            if lola_image.exists()
            else 0
        )

        check(
            "LOLA DEM exists",
            lola_image.exists(),
            str(lola_image),
        )

        check(
            "LOLA DEM size",
            (
                lola_image.exists()
                and actual_lola_size
                == expected_lola_size
            ),
            (
                f"expected={expected_lola_size} bytes, "
                f"actual={actual_lola_size} bytes"
            ),
        )

        terrain_horizons = []

        for name, result in results.items():

            sun_horizon = (
                result.sun.terrain_horizon_elevation
            )

            earth_horizon = (
                result.earth.terrain_horizon_elevation
            )

            check(
                f"{name}: Sun terrain horizon finite",
                (
                    sun_horizon is not None
                    and finite(sun_horizon)
                ),
                f"{sun_horizon}°",
            )

            check(
                f"{name}: Earth terrain horizon finite",
                (
                    earth_horizon is not None
                    and finite(earth_horizon)
                ),
                f"{earth_horizon}°",
            )

            if sun_horizon is not None:
                terrain_horizons.append(
                    round(sun_horizon, 10)
                )

            check(
                f"{name}: Sun terrain horizon range",
                (
                    sun_horizon is not None
                    and -90.0
                    <= sun_horizon
                    <= 90.0
                ),
                f"{sun_horizon}°",
            )

            check(
                f"{name}: Earth terrain horizon range",
                (
                    earth_horizon is not None
                    and -90.0
                    <= earth_horizon
                    <= 90.0
                ),
                f"{earth_horizon}°",
            )

            if result.sun.terrain_visible is not None:
                expected_sun_terrain_visibility = (
                    result.sun.elevation
                    > result.sun.terrain_horizon_elevation
                )

                check(
                    f"{name}: Sun terrain visibility consistent",
                    (
                        result.sun.terrain_visible
                        == expected_sun_terrain_visibility
                    ),
                    (
                        f"elevation="
                        f"{result.sun.elevation:.6f}°, "
                        f"horizon="
                        f"{result.sun.terrain_horizon_elevation:.6f}°, "
                        f"visible="
                        f"{result.sun.terrain_visible}"
                    ),
                )

            if result.earth.terrain_visible is not None:
                expected_earth_terrain_visibility = (
                    result.earth.elevation
                    > result.earth.terrain_horizon_elevation
                )

                check(
                    f"{name}: Earth terrain visibility consistent",
                    (
                        result.earth.terrain_visible
                        == expected_earth_terrain_visibility
                    ),
                    (
                        f"elevation="
                        f"{result.earth.elevation:.6f}°, "
                        f"horizon="
                        f"{result.earth.terrain_horizon_elevation:.6f}°, "
                        f"visible="
                        f"{result.earth.terrain_visible}"
                    ),
                )

        check(
            "LOLA terrain responds to site location",
            len(set(terrain_horizons)) > 1,
            f"Sun terrain horizons={terrain_horizons}",
        )

        # ------------------------------------------------
        # 9. DIFFERENT SITES MUST PRODUCE DIFFERENT
        #    LOCAL RESULTS
        # ------------------------------------------------

        print()
        print("8. LOCATION SENSITIVITY TEST")
        print("-" * 70)

        sun_elevations = [
            round(
                result.sun.elevation,
                10,
            )
            for result in results.values()
        ]

        earth_elevations = [
            round(
                result.earth.elevation,
                10,
            )
            for result in results.values()
        ]

        check(
            "Sun results respond to site location",
            len(set(sun_elevations)) > 1,
            f"Sun elevations={sun_elevations}",
        )

        check(
            "Earth results respond to site location",
            len(set(earth_elevations)) > 1,
            f"Earth elevations={earth_elevations}",
        )

        # ------------------------------------------------
        # 10. TIME SENSITIVITY TEST
        # ------------------------------------------------

        print()
        print("10. TIME SENSITIVITY TEST")
        print("-" * 70)

        test_site = next(
            iter(LANDING_SITES.values())
        )

        result_t1 = engine.analyze(
            test_site,
            t1,
        )

        result_t2 = engine.analyze(
            test_site,
            t2,
        )

        sun_time_changed = (
            abs(
                result_t1.sun.elevation
                - result_t2.sun.elevation
            )
            > 1e-8
            or
            abs(
                result_t1.sun.azimuth
                - result_t2.sun.azimuth
            )
            > 1e-8
        )

        earth_time_changed = (
            abs(
                result_t1.earth.elevation
                - result_t2.earth.elevation
            )
            > 1e-8
            or
            abs(
                result_t1.earth.azimuth
                - result_t2.earth.azimuth
            )
            > 1e-8
        )

        check(
            "Sun observation responds to time",
            sun_time_changed,
            (
                f"t1 elev/az="
                f"{result_t1.sun.elevation:.6f}/"
                f"{result_t1.sun.azimuth:.6f}; "
                f"t2="
                f"{result_t2.sun.elevation:.6f}/"
                f"{result_t2.sun.azimuth:.6f}"
            ),
        )

        check(
            "Earth observation responds to time",
            earth_time_changed,
            (
                f"t1 elev/az="
                f"{result_t1.earth.elevation:.6f}/"
                f"{result_t1.earth.azimuth:.6f}; "
                f"t2="
                f"{result_t2.earth.elevation:.6f}/"
                f"{result_t2.earth.azimuth:.6f}"
            ),
        )

        # ------------------------------------------------
        # 11. AZIMUTH RANGE
        # ------------------------------------------------

        print()
        print("11. GEOMETRIC RANGE CHECK")
        print("-" * 70)

        for name, result in results.items():

            check(
                f"{name}: Sun elevation range",
                -90 <= result.sun.elevation <= 90,
                f"{result.sun.elevation:.6f}°",
            )

            check(
                f"{name}: Earth elevation range",
                -90 <= result.earth.elevation <= 90,
                f"{result.earth.elevation:.6f}°",
            )

            check(
                f"{name}: Sun azimuth range",
                0 <= result.sun.azimuth < 360,
                f"{result.sun.azimuth:.6f}°",
            )

            check(
                f"{name}: Earth azimuth range",
                0 <= result.earth.azimuth < 360,
                f"{result.earth.azimuth:.6f}°",
            )

        # ------------------------------------------------
        # 12. REPEATABILITY TEST
        # ------------------------------------------------

        print()
        print("12. REPEATABILITY TEST")
        print("-" * 70)

        repeat1 = engine.analyze(
            test_site,
            t1,
        )

        repeat2 = engine.analyze(
            test_site,
            t1,
        )

        same = (
            abs(
                repeat1.sun.elevation
                - repeat2.sun.elevation
            ) < 1e-12
            and
            abs(
                repeat1.sun.azimuth
                - repeat2.sun.azimuth
            ) < 1e-12
            and
            abs(
                repeat1.earth.elevation
                - repeat2.earth.elevation
            ) < 1e-12
            and
            abs(
                repeat1.earth.azimuth
                - repeat2.earth.azimuth
            ) < 1e-12
        )

        check(
            "Same input produces same result",
            same,
        )

    except Exception as exc:

        check(
            "LunarAnalysisEngine execution",
            False,
            repr(exc),
        )

    finally:

        try:
            engine.unload()
        except Exception:
            pass

        spice.kclear()

    # --------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    print(f"PASS: {PASS}")
    print(f"FAIL: {FAIL}")

    if FAIL == 0:
        print()
        print("SCIENCE ENGINE STATUS: PASS")
        print()
        print("The tested observations are being generated from")
        print("the installed SPICE kernels and lunar geometry engine.")
        print()
        print("No mocked/static result was detected by this test.")
        print("=" * 70)
        return 0

    else:
        print()
        print("SCIENCE ENGINE STATUS: FAILED")
        print()
        print("At least one scientific integrity check failed.")
        print("Do not treat the current results as fully verified.")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
