import lxml.etree as xml
from operator import itemgetter
import numpy as np

COMPLEX_NODES = ['PlantModel', 'Drawing', 'Label', 'Nozzle', 'PipingNetworkSystem', 'PipeFlowArrow',
                 'PipingNetworkSegment', 'PipingComponent', 'Equipment', 'SignalLine', 'ActuatingSystem',
                 'ActuatingSystemComponent', 'InformationFlow',
                 'ProcessInstrumentationFunction', 'PipeConnectorSymbol']


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


def get_model_dimensions_from_plant_model(obj: xml._Element):
    """
    function to get drawing dimensions from PlantModel object
    :param obj:
    :return:
    """
    ensure_type(obj, 'PlantModel')

    plant_extent = obj.find('Extent')
    if plant_extent is None:
        raise AssertionError('Extent must be presented in PlantModel')

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
    recursive function to set position, rotation angle and scale of model elements taken from ShapeCatalogue
    # fixme provide support for all required types which are:
        Equipment +
        PipingComponent +
        Nozzle +
        ProcessInstrument
        InstrumentComponent
        Component
        PipeConnector
        SignalConnectorSymbol
        InsulationSymbol
        PropertyBreak
        Label
        PipeFlowArrow
    # todo support unit conversion with respect to Units attribute of ShapeCatalogue
    :param item: object model element
    :param pos_t: position tuple (x, y)
    :param ref_t: reference tuple (x, y)
    :param scale_t: scale tuple (x,y,z)
    :return:
    """

    # temporary to set breakpoint on circles
    if item.tag == 'Circle':
        print('got circle')

    # scaling
    scale_m = np.array([[scale_t[0], 0], [0, scale_t[1]]])

    # rotating
    # The Reference is defined by the cosine and sine of the rotation angle. The x-value contains the cosine,
    # the y-value the sine of the rotation angle, with the rotation being measured anti-clockwise. In consequence
    # x^2 + y^2 = 1 must be fullfilled in order for the values to be correct.
    if abs(1 - (ref_t[0]**2 + ref_t[1]**2)) > 0.0001:
        raise AssertionError("x^2 + y^2 = 1 must be full-filled in order for the reference values to be correct.")
    c, s = float(ref_t[0]), float(ref_t[1])
    rotation_m = np.array(((c, -s), (s, c)))

    def apply_transformation_to_coordinates_2d(obj_to_apply):
        """
        applies scale and rotation transfomation to X,Y points in provided object
        :param obj_to_apply: XML node with attributes X and Y
        :return:
        """
        point_m = np.array([float(obj_to_apply.attrib['X']), float(obj_to_apply.attrib['Y'])])
        new_coords = scale_m.dot(point_m)
        r_cords = rotation_m.dot(new_coords)
        obj_to_apply.attrib['X'] = str(pos_t[0] + r_cords[0])
        obj_to_apply.attrib['Y'] = str(pos_t[1] + r_cords[1])

    if item.find('Position') is not None:
        loc = item.find('Position').find('Location')
        apply_transformation_to_coordinates_2d(loc)

    for coordinate in item.findall('Coordinate'):
        apply_transformation_to_coordinates_2d(coordinate)

    # fixme need to find how to scale radius of a circle
    if item.attrib.get('Radius') is not None:
        item.attrib['Radius'] = str(float(item.attrib['Radius']) * scale_m[0][0])

    for child in item:
        set_scale_angle_pos(child, pos_t, ref_t, scale_t)


def set_line_type(item, line_type):
    """
    function to set line type to a Proteus object
    :param item: Proteus object with Presentation child
    :param line_type: See Proteus reference for available line types
    :return: None
    """
    if item.find('Presentation') is not None:
        item.find('Presentation').attrib['LineType'] = line_type


def set_line_weight(item, line_weight):
    """
    function to set line type to a Proteus object
    :param item: Proteus object with Presentation child
    :param line_type: See Proteus reference for available line types
    :return: None
    """
    if item.find('Presentation') is not None:
        item.find('Presentation').attrib['LineWeight'] = line_weight


def process_shape_reference(node, shape_reference, ctx):
    """
    function to process an object from ShapeCatalogue referenced  by given node
    and used to set correct position, scale and rotation angle
    :param node: Proteus XML object
    :param shape_reference: XML object fetched from ShapeCatalogue where tag is equal to node.tag and ComponentName
    attribute is equal to node ComponentName attribute.
    :param ctx: drawing context
    :return: None
    """
    if shape_reference is not None:
        pos_x, pos_y = map(lambda x: float(x) * ctx.units.value,
                           itemgetter('X', 'Y')(node.find('Position').find('Location').attrib))
        ref_x, ref_y = map(lambda x: float(x) * ctx.units.value,
                           itemgetter('X', 'Y')(node.find('Position').find('Reference').attrib))
        scale_x, scale_y, scale_z = map(lambda x: float(x) * ctx.units.value,
                                        itemgetter('X', 'Y', 'Z')(node.find('Scale').attrib)) if node.find(
            'Scale') is not None else (1, 1, 1)
        idx = 1
        for item in shape_reference:
            if item.tag in ['Presentation', 'Extent', 'Position', 'GenericAttributes', 'Min', 'Max']:
                continue
            set_scale_angle_pos(item, (pos_x, pos_y), (ref_x, ref_y), (scale_x, scale_y, scale_z))
            node.insert(idx, item)
            idx += 1
