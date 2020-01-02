"""
Contains handler functions for Proteus -> SVG conversion for different Proteus elements
a handler function must take 2 arguments
    * xml.etree.ElementTree.Element with Proteus definition
    * model context
and return corresponding svgwrite object
"""

import xml.etree.ElementTree as XMLParse
from operator import itemgetter
from typing import Callable
import svgwrite
from proteus_utils import ensure_type
from color_utils import fetch_color_from_presentation
from model_context import Context
from line_utils import fetch_line_type_from_presentation


def resolve_node_handler(node_type: str) -> Callable:
    """
    function to find and return a handler for Proteus node
    :param node_type: string value of node type (simply tag name)
    :return: Callable handler object
    """
    if 'Line' == node_type:
        return line_handler
    elif 'Text2' == node_type:
        return text_handler
    elif 'Circle' == node_type:
        return circle_handler
    return dummy_handler
    # raise NotImplementedError(f'handler for {node_type} is not implemented yet')


def line_handler(node: XMLParse.Element, ctx: Context) -> svgwrite.shapes.Line:
    """
    handler to transform Proteus line object to SVG line object
    :param node: XML node with Proteus line definition
    :param ctx: Proteus model context
    :return: SVG line object
    """
    ensure_type(node, 'Line')
    coordinates = node.findall('Coordinate')

    if len(coordinates) != 2:
        raise AssertionError(f'a line must have a pair of coordinates, {len(coordinates)} found')

    presentation_obj = node.find("Presentation")

    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    stroke_color = fetch_color_from_presentation(presentation_obj)
    stroke_width = float(presentation_obj.attrib.get('LineWeight'))

    x_min, y_min = itemgetter('X', 'Y')(coordinates[0].attrib)
    x_max, y_max = itemgetter('X', 'Y')(coordinates[1].attrib)

    line = svgwrite.shapes.Line(start=(float(x_min), ctx.y_max - float(y_min)),
                                end=(float(x_max), ctx.y_max - float(y_max)), stroke=stroke_color,
                                style=f'stroke-width:{stroke_width}')

    line_type = fetch_line_type_from_presentation(presentation_obj)
    if line_type:
        line.dasharray(line_type)
    return line


def centerline_handler(node: XMLParse.Element, ctx: Context) -> svgwrite.path.Path:
    ensure_type(node, 'CenterLine')

    presentation_obj = node.find("Presentation")
    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    coordinates = node.findall('Coordinate')

    path = svgwrite.path.Path()

    for coordinate in coordinates:
        x_, y_ = itemgetter('X', 'Y')(coordinate.attrib)


def text_handler(node: XMLParse.Element, ctx: Context) -> svgwrite.text.Text:
    """
    handler to transform Proteus Text object to SVG String object
    :param node: XML node with Proteus line definition
    :param ctx: Proteus model context
    :return: SVG line object
    """
    ensure_type(node, 'Text')

    if node.attrib.get('String'):
        text_arr = node.attrib.get('String').split('\\n')
    else:
        return
    text_font = node.attrib.get('Font')
    text_size = round(float(node.attrib.get('Height')) * 10) / 10
    style = f'font-size:{text_size}px; font-family:{text_font}'

    text_justification = node.attrib.get('Justification')
    if not text_justification:
        text_justification = 'LeftBottom'

    if 'Left' in text_justification:
        svg_jst = 'start'
    elif 'Right' in text_justification:
        svg_jst = 'end'
    elif 'Center' in text_justification:
        svg_jst = 'middle'

    add_y = 0
    if 'Top' in text_justification:
        add_y = text_size

    text_pos_x, text_pos_y = itemgetter('X', 'Y')(node.find('Position').find('Location').attrib)

    text_obj = svgwrite.text.Text(text_arr[0], x=[float(text_pos_x)],
                                  y=[ctx.y_max - float(text_pos_y) + text_size], style=style,
                                  text_anchor=svg_jst)

    for span in text_arr[1:]:
        t_span = svgwrite.text.TSpan(span, x=[float(text_pos_x)], dy=[text_size], text_anchor=svg_jst)
        text_obj.add(t_span)

    return text_obj


def circle_handler(node: XMLParse.Element, ctx: Context) -> svgwrite.shapes.Circle:
    ensure_type(node, 'Circle')
    presentation_obj = node.find("Presentation")

    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    stroke_color = fetch_color_from_presentation(presentation_obj)
    stroke_width = float(presentation_obj.attrib.get('LineWeight'))
    radius = float(node.attrib.get('Radius'))
    coordinates = node.find('Position').find('Location')
    x_pos, y_pos = itemgetter('X', 'Y')(coordinates.attrib)

    circle = svgwrite.shapes.Circle((float(x_pos), ctx.y_max - float(y_pos)), radius, fill='none', stroke=stroke_color,
                                    style=f'stroke-width:{stroke_width}')

    return circle


def dummy_handler(node: XMLParse.Element, ctx: Context) -> None:
    """
    special case handler that process nothing and returns None
    :param node: node to process
    :param ctx: model context
    :return: always None
    """
    return None
