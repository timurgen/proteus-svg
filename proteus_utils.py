import xml.etree.ElementTree as XMLParse


def ensure_type(obj: XMLParse.Element, tag: str):
    """
    function to check tag name for given element
    :param obj: object to check
    :param tag: type object must match
    :return: raises ValueError if type mismatched and return nothing otherwise
    """
    if type(obj) is not XMLParse.Element:
        raise ValueError(f'xml.etree.ElementTree.Element expected {type(obj)} found')
    if obj.tag != tag:
        raise ValueError(f'wrong type: expected type {tag}, got type {obj.tag}')
