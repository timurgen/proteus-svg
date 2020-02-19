import lxml.etree as xml
from operator import itemgetter

COMPLEX_NODES = ['PlantModel', 'Drawing', 'Label', 'Nozzle', 'PipingNetworkSystem', 'PipeFlowArrow',
                 'PipingNetworkSegment', 'PipingComponent', 'Equipment', 'SignalLine', 'ActuatingSystem',
                 'ActuatingSystemComponent', 'InformationFlow',
                 'ProcessInstrumentationFunction']


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


def get_gen_attr_val(node, _set, attr):
    """
    function to get a value of generic attribute 'attr' that belongs to given generic attributes set
    :param node: source node
    :param _set: generic attributes set name
    :param attr: attribute name
    :return: value of given attribute or None if not found
    """
    gen_attr = node.find(f'.//GenericAttributes[@Set="{_set}"]/GenericAttribute[@Name="{attr}"]')
    if gen_attr is not None:
        return gen_attr.attrib.get('Value').strip()
    return None


def should_process_child(node_type: str) -> bool:
    """
    function that returns True if child of given node type should be processed
    :param node_type: name of XmpLant object
    :return: True if child objects should be processed or False otherwise
    """
    return node_type in COMPLEX_NODES


def set_scale_angle_pos(item, pos_t, ref_t, scale_t):
    """
    recursive function to set position, rotation angle and scale of model taken from ShapeCatalogue
    :param item: object model
    :param pos_t: position tuple (x, y)
    :param ref_t: reference tuple (x, y)
    :param scale_t: scale tuple (x,y,z)
    :return:
    """
    if item.find('Position') is not None:
        loc = item.find('Position').find('Location')
        loc.attrib['X'] = str(pos_t[0] + float(loc.attrib['X']))
        loc.attrib['Y'] = str(pos_t[1] + float(loc.attrib['Y']))

    for coordinate in item.findall('Coordinate'):
        coordinate.attrib['X'] = str(pos_t[0] + float(coordinate.attrib['X']))
        coordinate.attrib['Y'] = str(pos_t[1] + float(coordinate.attrib['Y']))

    # todo rotation angle
    cos_phi = ref_t[0]
    sin_phi = ref_t[1]

    if abs(1 - (cos_phi ** 2 + sin_phi ** 2)) > 0.0001:
        raise ValueError("Reference x**2 + y**2 must be equal to 1")
    # todo scaling

    for child in item:
        set_scale_angle_pos(child, pos_t, ref_t, scale_t)


def set_line_type(item, line_type):
    if item.find('Presentation') is not None:
        item.find('Presentation').attrib['LineType'] = line_type


def set_line_weight(item, line_weight):
    if item.find('Presentation') is not None:
        item.find('Presentation').attrib['LineWeight'] = line_weight
