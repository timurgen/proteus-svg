import svgwrite
import logging
import sys
import xml.etree.ElementTree as XMLParse
from model_context import Context
from svg_utils import get_default, add_grid
from handlers import resolve_node_handler, extent_handler
from proteus_utils import get_model_dimensions_from_plant_model, should_process_child

ROOT_ELEMENT = 'PlantModel'
DEBUG = False


def process_node(node: XMLParse.Element, target: svgwrite.base.BaseElement, model_ctx: Context):
    node_type = node.tag
    logging.debug(f'processing {node_type} node')

    node_handler = resolve_node_handler(node_type)
    result = node_handler(node, model_ctx)

    if result:
        target.add(result)
        if DEBUG:
            extent_obj = node.find('Extent')
            extent_rect = extent_handler(extent_obj, model_ctx)
            target.add(extent_rect)
    if should_process_child(node.tag):
        for child in list(node):
            process_node(child, result if result else target, model_ctx)


if __name__ == '__main__':
    # input and output files
    #input_file_name = '080.xml'
    #input_file_name = '2601-01.xml'
    input_file_name = 'text_curve.xml'
    input_file = XMLParse.parse(input_file_name)

    # set up logging
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # root element for Proteus files is always "PlantModel"
    plant_model = input_file.getroot()

    if plant_model.tag != ROOT_ELEMENT:
        logging.critical(f'malformed file {input_file_name}, {ROOT_ELEMENT} expected at root level')
        sys.exit(1)

    pl_info = plant_model.find('PlantInformation')

    # get model dimension borders
    (min_x, min_y, max_x, max_y) = get_model_dimensions_from_plant_model(plant_model)

    drawing = get_default(f'{input_file_name}.svg')
    model_context = Context(min_x, max_x, min_y, max_y, pl_info.attrib['OriginatingSystem'], pl_info.attrib['Units'])

    drawing.attribs['width'] = model_context.x_max
    drawing.attribs['height'] = model_context.y_max

    add_grid(drawing, 10)

    # process Proteus data recursively
    process_node(plant_model, drawing, model_context)

    # final statement
    drawing.save()
