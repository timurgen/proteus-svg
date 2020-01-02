"""
utility functions to manipulate color values
"""
from typing import Tuple
import math
import xml.etree.ElementTree as XMLParse
from operator import itemgetter
from proteus_utils import ensure_type


def rgb_to_hex_string(red: int, green: int, blue: int) -> str:
    """
    function to convert RGB values to hex string
    :param red: Red color value
    :param green: Green color value
    :param blue: Blue color value
    :return: color value presented as hex string
    """
    if not 0 <= red <= 255:
        raise ValueError(f"R component out of range ({red})")

    if not 0 <= green <= 255:
        raise ValueError(f"G component out of range ({green})")

    if not 0 <= blue <= 255:
        raise ValueError(f"B component out of range ({blue})")
    return '#' + ''.join('{:02X}'.format(a) for a in [red, green, blue])


def compute_rgb(red: float, green: float, blue: float) -> Tuple[int, int, int]:
    """
    function to compute RGB values from Proteus RGB values
    :param red: Red color presented as double number from 0.0 to 1.0
    :param green: Green color presented as double number from 0.0 to 1.0
    :param blue: Blue color presented as double number from 0.0 to 1.0
    :return: RGB values supported by SVG (0-255)
    """
    if not 0.0 <= red <= 1.0:
        raise ValueError(f"R component out of range ({red})")

    if not 0.0 <= green <= 1.0:
        raise ValueError(f"G component out of range ({green})")

    if not 0.0 <= blue <= 1.0:
        raise ValueError(f"B component out of range ({blue})")

    return math.floor(red * 255), math.floor(green * 255), math.floor(blue * 255)


def fetch_color_from_presentation(pr_obj: XMLParse.Element) -> str:
    """
    function to fetch color from Presentation object
    :param pr_obj: Presentation object with 'R', 'G','B' objects defined
    :return: color as hex string
    """
    ensure_type(pr_obj, 'Presentation')
    red, green, blue = map(float, itemgetter('R', 'G', 'B')(pr_obj.attrib))
    return rgb_to_hex_string(*compute_rgb(red, green, blue))
