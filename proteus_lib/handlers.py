"""
Contains handler functions for Proteus -> SVG conversion for different Proteus elements
a handler function must take 2 arguments
    * xml.etree.ElementTree.Element with Proteus definition
    * model context
and return corresponding svgwrite object
"""
import logging

from operator import itemgetter
from typing import Callable
import svgwrite
from lxml import etree as xml

from proteus_lib.proteus_utils import ensure_type, should_process_child
from proteus_lib.color_utils import fetch_color_from_presentation
from proteus_lib.model_context import Context
from proteus_lib.line_utils import fetch_line_type_from_presentation
from proteus_lib.svg_utils import describe_arc


def resolve_node_handler(node_type: str) -> Callable:
    """
    function to find and return a handler for Proteus node
    :param node_type: string value of node type (simply tag name)
    :return: Callable handler object
    """
    if node_type in ['Connection','PlantModel', 'PlantInformation', 'Extent', 'Presentation', 'Label', 'ShapeCatalogue', 'Position',
                     'Nozzle', 'Scale', 'PersistentID', 'GenericAttributes', 'ConnectionPoints', 'PipingNetworkSystem',
                     'PipeFlowArrow', 'PipingNetworkSegment', 'PipingComponent', 'SignalLine']:
        return dummy_handler

    if 'Line' == node_type:
        return line_handler
    elif 'CenterLine' == node_type:
        return centerline_handler
    elif 'Text' == node_type:
        return text_handler
    elif 'Circle' == node_type:
        return circle_handler
    elif 'Drawing' == node_type:
        return drawing_handler
    elif 'TrimmedCurve' == node_type:
        return trimmed_curve_handler
    elif 'Equipment' == node_type:
        # return equipment_handler
        return dummy_handler
    raise NotImplementedError(f'handler for {node_type} is not implemented yet')


def line_handler(node: xml.Element, ctx: Context) -> svgwrite.shapes.Line:
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

    x_min_str, y_min_str = itemgetter('X', 'Y')(coordinates[0].attrib)
    x_max_str, y_max_str = itemgetter('X', 'Y')(coordinates[1].attrib)

    x_min_f, y_min_f, x_max_f, y_max_f = map(float, (x_min_str, y_min_str, x_max_str, y_max_str))

    line = svgwrite.shapes.Line(start=(x_min_f, ctx.y_max - y_min_f),
                                end=(x_max_f, ctx.y_max - y_max_f),
                                stroke=stroke_color,
                                style=f'stroke-width:{stroke_width}')

    line_type = fetch_line_type_from_presentation(presentation_obj)
    if line_type:
        line.dasharray(line_type)
    return line


def centerline_handler(node: xml.Element, ctx: Context) -> svgwrite.path.Path:
    ensure_type(node, 'CenterLine')

    presentation_obj = node.find("Presentation")
    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    stroke_color = fetch_color_from_presentation(presentation_obj)
    stroke_width = float(presentation_obj.attrib.get('LineWeight'))

    coordinates = node.findall('Coordinate')
    is_filled = True if node.attrib.get('Filled') else False
    path = svgwrite.path.Path(None, stroke=stroke_color,
                              fill='none' if not is_filled else stroke_color,
                              style=f'stroke-width:{stroke_width}')

    start_point = True
    for coordinate in coordinates:
        operation = 'M' if start_point else 'L'
        start_point = False
        x_, y_ = itemgetter('X', 'Y')(coordinate.attrib)
        path.push(operation, float(x_), ctx.y_max - float(y_))

    line_type = fetch_line_type_from_presentation(presentation_obj)
    if line_type:
        path.dasharray(line_type)

    return path


def text_handler(node: xml.Element, ctx: Context) -> svgwrite.text.Text:
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

    if text_justification.startswith('Left'):
        svg_jst = 'start'
    elif text_justification.startswith('Right'):
        svg_jst = 'end'
    elif text_justification.startswith('Center'):
        svg_jst = 'middle'
    else:
        raise ValueError(f'Unknown justification {text_justification}')

    # fixme
    add_y = 0
    if text_justification.endswith('Top'):
        add_y = 1
    elif text_justification.endswith('Center'):
        add_y = 1
    elif text_justification.endswith('Bottom'):
        add_y = 1
    else:
        raise ValueError(f'Unknown justification {text_justification}')

    text_pos_x, text_pos_y = map(lambda x: float(x) * ctx.units.value,
                                 itemgetter('X', 'Y')(node.find('Position').find('Location').attrib))

    text_obj = svgwrite.text.Text(text_arr[0], x=[text_pos_x],
                                  y=[ctx.y_max - text_pos_y + text_size - add_y], style=style,
                                  text_anchor=svg_jst)

    for span in text_arr[1:]:
        t_span = svgwrite.text.TSpan(span, x=[float(text_pos_x)], dy=[text_size - add_y], text_anchor=svg_jst)
        text_obj.add(t_span)

    return text_obj


def circle_handler(node: xml.Element, ctx: Context) -> svgwrite.shapes.Circle:
    """
    handler to transform Proteus Circle object to SVG Circle object
    :param node: XML node with Proteus circle definition
    :param ctx: Proteus model context
    :return: SVG Circle object
    """
    ensure_type(node, 'Circle')
    presentation_obj = node.find("Presentation")

    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    stroke_color = fetch_color_from_presentation(presentation_obj)
    stroke_width = float(presentation_obj.attrib.get('LineWeight'))
    radius = float(node.attrib.get('Radius'))
    is_filled = True if node.attrib.get('Filled') else False
    coordinates = node.find('Position').find('Location')
    x_pos, y_pos = itemgetter('X', 'Y')(coordinates.attrib)

    circle = svgwrite.shapes.Circle((float(x_pos), ctx.y_max - float(y_pos)), radius,
                                    fill='none' if not is_filled else stroke_color,
                                    stroke=stroke_color,
                                    style=f'stroke-width:{stroke_width}')

    return circle


def extent_handler(node: xml.Element, ctx: Context) -> svgwrite.shapes.Rect:
    """
    handler to transform Proteus Extent object to SVG Circle object
    :param node: XML node with Proteus extent definition
    :param ctx: Proteus model context
    :return: SVG Rect object
    """
    ensure_type(node, 'Extent')
    stroke_width = 0.1
    x_min_str, y_min_str = itemgetter('X', 'Y')(node.find('Min').attrib)
    x_max_str, y_max_str = itemgetter('X', 'Y')(node.find('Max').attrib)

    x_min_f, y_min_f, x_max_f, y_max_f = map(float, (x_min_str, y_min_str, x_max_str, y_max_str))
    y_min_f = ctx.y_max - y_min_f
    y_max_f = ctx.y_max - y_max_f
    rect_width = x_max_f - x_min_f
    rect_height = y_min_f - y_max_f
    return svgwrite.shapes.Rect((x_min_f, y_min_f - rect_height), (rect_width, rect_height),
                                stroke='red',
                                fill='none',
                                style=f'stroke-width:{stroke_width}',
                                onmouseover='evt.target.setAttribute("fill", "blue")',
                                onmouseout='evt.target.setAttribute("fill", "none")')


def equipment_handler(node: xml.Element, ctx: Context) -> svgwrite.shapes.Rect:
    """
    special case handler that process nothing and returns None
    :param node: node to process
    :param ctx: model context
    :return: always None
    """
    extent_rect = extent_handler(node.find('Extent'), ctx)
    return extent_rect


def drawing_handler(node: xml.Element, ctx: Context) -> svgwrite.container.Group:
    return svgwrite.container.Group()


def trimmed_curve_handler(node: xml.Element, ctx: Context):
    def process_circle(circle_node: xml.Element):
        ensure_type(circle_node, 'Circle')
        _presentation_obj = circle_node.find('Presentation')
        _radius = circle_node.attrib.get('Radius')
        _x, _y = itemgetter('X', 'Y')(circle_node.find('Position').find('Location').attrib)
        _stroke_color = fetch_color_from_presentation(_presentation_obj)
        _stroke_width = float(_presentation_obj.attrib.get('LineWeight'))
        return _x, _y, _radius, _stroke_color, _stroke_width

    def process_ellipse(ellipse_node: xml.Element):
        raise NotImplementedError('handler for ellipse is not implemented yet')

    x, y, radius, stroke_color, stroke_width = process_circle(node.find('Circle')) if node.find(
        'Circle') else process_ellipse(node.find('Ellipse'))

    start_angle, end_angle = map(float, itemgetter('StartAngle', 'EndAngle')(node.attrib))

    d = describe_arc(float(x), float(ctx.y_max - float(y)), float(radius), start_angle, end_angle)
    path = svgwrite.path.Path(d, stroke=stroke_color, fill='none', style=f'stroke-width:{stroke_width}')
    path.translate(0, ctx.y_max)
    path.scale(1, -1)
    return path


def dummy_handler(node: xml.Element, ctx: Context) -> None:
    """
    special case handler that process nothing and returns None
    :param node: node to process
    :param ctx: model context
    :return: always None
    """
    return None


def process_node(node: xml.Element, target: svgwrite.base.BaseElement, model_ctx: Context):
    node_type = node.tag
    logging.debug(f'processing {node_type} node')

    node_handler = resolve_node_handler(node_type)
    result = node_handler(node, model_ctx)

    if result:
        target.add(result)
        if model_ctx.debug:
            extent_obj = node.find('Extent')
            extent_rect = extent_handler(extent_obj, model_ctx)
            target.add(extent_rect)
    if should_process_child(node.tag):
        for child in list(node):
            process_node(child, result if result else target, model_ctx)