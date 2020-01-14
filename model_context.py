from dataclasses import dataclass
import svgwrite


@dataclass
class Context:
    x_min: int
    x_max: int
    y_min: int
    y_max: int
    origin: str = None
    units: str = "mm"
