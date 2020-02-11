import lxml.etree as xml
from operator import itemgetter


def ensure_type(obj: xml.Element, tag: str):
    """
    function to check tag name for given element
    :param obj: object to check
    :param tag: type object must match
    :return: raises ValueError if type mismatched and return nothing otherwise
    """
    if type(obj) is not xml._Element:
        raise ValueError(f'xml.etree.ElementTree.Element expected {type(obj)} found')
    if obj.tag != tag:
        raise ValueError(f'wrong type: expected type {tag}, got type {obj.tag}')


def get_model_dimensions_from_plant_model(obj: xml.Element):
    ensure_type(obj, 'PlantModel')
    plant_extent = obj.find('Extent')
    (min_x_str, min_y_str) = itemgetter('X', 'Y')(plant_extent.find('Min').attrib)
    (max_x_str, max_y_str) = itemgetter('X', 'Y')(plant_extent.find('Max').attrib)
    return map(float, (min_x_str, min_y_str, max_x_str, max_y_str))


def should_process_child(node_type: str) -> bool:
    return node_type in ['PlantModel', 'Drawing', 'Label', 'Nozzle', 'PipingNetworkSystem', 'PipeFlowArrow',
                         'PipingNetworkSegment', 'Equipment', 'SignalLine']
