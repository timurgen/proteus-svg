from proteus_utils import ensure_type
import xml.etree.ElementTree as XMLParse


def fetch_line_type_from_presentation(pr_obj: XMLParse.Element) -> list:
    """
    function to fetch and convert Proteus line type to SVG stroke-dasharray
    One of the numbers or names from the following (Object Model document v2.2) :-
    0 Solid
    1 Dotted
    2 Dashed
    3 Long Dash
    4 Long Dash + Short Dash, CenterLine
    5 Short Dash
    6 Long Dash + Short Dash + Short Dash
    7 Dash + Short Dash
    :param pr_obj: Presentation object
    :return: list values for stroke-dasharray SVG property
    """
    ensure_type(pr_obj, 'Presentation')
    line_type = int(pr_obj.attrib.get('LineType'))
    if 0 == line_type:
        return []
    if 1 == line_type:
        return [1]
    if 2 == line_type:
        return [3]
    if 3 == line_type:
        return [4, 1]
    if 4 == line_type:
        return [4, 1, 2, 1]
    if 5 == line_type:
        return [2, 1]
    if 6 == line_type:
        return [4, 1, 2, 1, 2, 1]
    if 7 == line_type:
        return [3, 1, 2, 1]
    raise ValueError(f'unknown line type ({line_type}) found')
