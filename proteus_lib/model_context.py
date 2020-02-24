from dataclasses import dataclass
from enum import Enum
import lxml.etree as xml
from copy import deepcopy

import svgwrite


@dataclass
class Unit(Enum):
    mm = 1
    Metre = 1000


@dataclass
class Context:
    drawing: svgwrite.Drawing
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    origin: str = None
    debug: bool = False
    units: Unit = Unit.mm
    shape_catalog: xml._Element = None

    def get_from_shape_catalog(self, node_type, component_name):
        """
        Method to find if a symbol fo given type and component name exists in the shape catalogue
        :param node_type:
        :param component_name:
        :return: xml._Element if found or None otherwise
        """
        if self.shape_catalog is not None:
            return deepcopy(self.shape_catalog.find(f'.//{node_type}[@ComponentName="{component_name}"]'))
        return None

    def attributes_to_add_from_origin(self):
        """
        Method to map originating system to values that need to be extracted from GenericAttributes
        :return:
        """
        _origin = self.origin.lower()
        if _origin == 'comos':
            return [{'set': 'ComosProperties', 'values': ['Label', 'FullLabel']}]
