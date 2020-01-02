from dataclasses import dataclass


@dataclass
class Context:
    x_min: int
    x_max: int
    y_min: int
    y_max: int
