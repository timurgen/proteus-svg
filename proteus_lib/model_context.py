from dataclasses import dataclass
from enum import Enum

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
