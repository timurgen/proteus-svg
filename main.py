import svgwrite
import logging
import sys
import xml.etree.ElementTree as XMLParse
from operator import itemgetter
from color_utils import fetch_color_from_presentation
from proteus_utils import ensure_type
from line_utils import fetch_line_type_from_presentation
from model_context import Context
from svg_utils import get_default
from handlers import resolve_node_handler

ROOT_ELEMENT = 'PlantModel'


def process_line(node: XMLParse.Element) -> svgwrite.shapes.Line:
    ensure_type(node, 'Line')
    coordinates = node.findall('Coordinate')

    if len(coordinates) != 2:
        raise AssertionError(f'a line must have a pair of coordinates, {len(coordinates)} found')

    presentation_obj = node.find("Presentation")

    if presentation_obj is None:
        raise AssertionError(f'"Presentation" node expected but not found in Line node')

    stroke_color = fetch_color_from_presentation(presentation_obj)
    line_type = fetch_line_type_from_presentation(presentation_obj)
    x_min, y_min = itemgetter('X', 'Y')(coordinates[0].attrib)
    x_max, y_max = itemgetter('X', 'Y')(coordinates[1].attrib)
    line = svgwrite.shapes.Line(start=(float(x_min), 594 - float(y_min)),
                                end=(float(x_max), 594 - float(y_max)), stroke=stroke_color, style=f'stroke-width:0.25')
    if line_type:
        line.dasharray(line_type)
    return line


def process_node(node: XMLParse.Element, target: svgwrite.base.BaseElement, model_ctx: Context):
    node_type = node.tag
    logging.debug(f'processing {node_type} node')

    node_handler = resolve_node_handler(node_type)
    result = node_handler(node, model_ctx)

    if result:
        target.add(result)

    for child in list(node):
        process_node(child, target, model_ctx)


if __name__ == '__main__':
    # input and output files
    # input_file_name = '080.xml'
    input_file_name = '2601-01.xml'
    input_file = XMLParse.parse(input_file_name)

    # set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # root element for Proteus files is always "PlantModel"
    plant_model = input_file.getroot()

    if plant_model.tag != ROOT_ELEMENT:
        logging.critical(f'malformed file {input_file_name}, {ROOT_ELEMENT} expected at root level')
        sys.exit(1)

    plant_information = plant_model.find('PlantInformation')
    plant_extent = plant_model.find('Extent')

    # get model dimension borders
    (min_x, min_y) = itemgetter('X', 'Y')(plant_extent.find('Min').attrib)
    (max_x, max_y) = itemgetter('X', 'Y')(plant_extent.find('Max').attrib)
    model_context = Context(int(min_x), int(max_x), int(min_y), int(max_y))

    drawing = get_default(f'{input_file_name}.svg')
    drawing.attribs['width'] = model_context.x_max
    drawing.attribs['height'] = model_context.y_max

    # process Proteus data recursively
    process_node(plant_model, drawing, model_context)

    # final statement
    drawing.save()
