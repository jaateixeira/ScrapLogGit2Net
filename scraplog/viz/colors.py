"""
Node colors for organizations that are not in a color map.

The color comes from the organization name, so the same organization gets
the same color in every run, every figure and both visualizers (nofi and
nofo). Saturation and brightness are kept away from gray, which the
visualizers use for "others" and unknown organizations.
"""

import colorsys
import hashlib
from typing import Tuple


def organization_color(name: str) -> Tuple[float, float, float]:
    """Return an RGB color (each channel in [0, 1]) derived from the organization name."""
    digest = hashlib.sha256(name.encode("utf-8")).digest()
    hue = int.from_bytes(digest[0:4], "big") / 2**32
    saturation = 0.55 + 0.30 * digest[4] / 255
    value = 0.65 + 0.25 * digest[5] / 255
    return colorsys.hsv_to_rgb(hue, saturation, value)
