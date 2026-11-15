from app.core.models import Site


LANDING_SITES = {
    "Shackleton Crater": Site(
        name="Shackleton Crater",
        latitude=-89.67,
        longitude=129.78,
    ),
    "Cabeus Crater": Site(
        name="Cabeus Crater",
        latitude=-85.42,
        longitude=35.66,
    ),
    "Malapert Massif": Site(
        name="Malapert Massif",
        latitude=-85.99,
        longitude=0.00,
    ),
}

# Reference landing-site elevation used for mission-site reporting.
#
# These values are separate from the per-pixel LOLA terrain heights.
LANDING_SITE_HEIGHTS_KM = {
    "Shackleton Crater": 0.640898,
    "Cabeus Crater": 0.640898,
    "Malapert Massif": 0.640898,
}

