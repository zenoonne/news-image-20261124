"""Simplified world continents as lon/lat polygons, plus an equirectangular
projection helper.  Coordinates are hand-drawn and crude on purpose: the map
only has to read as "the world" at thumbnail size, not pass a survey check.
"""

# Each continent is a list of (lon, lat) vertices.
CONTINENTS = {
    "north_america": [
        (-168, 65), (-150, 70), (-120, 72), (-95, 72), (-80, 70), (-62, 60),
        (-55, 48), (-70, 44), (-80, 30), (-97, 26), (-105, 22), (-115, 30),
        (-124, 40), (-130, 55), (-155, 60), (-168, 65),
    ],
    "greenland": [
        (-45, 60), (-22, 68), (-20, 78), (-40, 83), (-60, 80), (-58, 66),
        (-45, 60),
    ],
    "south_america": [
        (-81, 8), (-70, 11), (-60, 10), (-50, 0), (-35, -6), (-38, -18),
        (-48, -25), (-58, -35), (-68, -55), (-75, -46), (-72, -30),
        (-70, -18), (-78, -8), (-81, 8),
    ],
    "africa": [
        (-17, 15), (-17, 28), (-5, 36), (12, 37), (32, 32), (43, 12),
        (51, 10), (45, -12), (40, -20), (25, -34), (18, -30), (12, -18),
        (9, -1), (9, 5), (-10, 5), (-17, 15),
    ],
    "europe": [
        (-10, 36), (-9, 44), (-2, 48), (2, 51), (5, 58), (12, 58),
        (20, 70), (30, 70), (40, 66), (40, 50), (30, 45), (26, 40),
        (18, 40), (12, 38), (0, 38), (-10, 36),
    ],
    "asia": [
        (40, 50), (40, 66), (70, 72), (110, 74), (140, 70), (160, 60),
        (145, 50), (135, 35), (122, 25), (110, 20), (100, 14), (92, 20),
        (80, 8), (72, 20), (60, 25), (48, 38), (40, 50),
    ],
    "australia": [
        (114, -22), (125, -14), (140, -12), (153, -25), (150, -38),
        (140, -38), (128, -32), (114, -22),
    ],
}

# Lat range we keep on the map (crops Antarctica and the empty far north).
LAT_TOP = 84.0
LAT_BOTTOM = -58.0


def make_projector(x0, y0, x1, y1):
    """Return project(lon, lat) -> (px, py) for a map box."""
    w = x1 - x0
    h = y1 - y0

    def project(lon, lat):
        px = x0 + (lon + 180.0) / 360.0 * w
        py = y0 + (LAT_TOP - lat) / (LAT_TOP - LAT_BOTTOM) * h
        return (px, py)

    return project
