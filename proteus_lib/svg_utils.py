import svgwrite
import math

from proteus_lib.color_utils import fetch_color_from_presentation
from proteus_lib.model_context import Context


def get_default(out_file_name, size, view_box, debug=False) -> svgwrite.Drawing:
    """
    creates and return SVG drawing element with default properties

    <svg version="1.1" width="500%" height="500%" style="" xmlns="http://www.w3.org/2000/svg" overflow="scroll">
     <defs>
      <filter id="glow" x="-40%" y="-40%" width="200%" height="200%">
       <feOffset result="offOut" in="SourceGraphic" dx="0" dy="0" />
       <feGaussianBlur result="blurOut" in="offOut" stdDeviation="2" />
       <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
      </filter>
      <style />
     </defs>
    </svg>

    :param view_box:
    :param size:
    :param debug: if svgwrite should be initialized in debug mode
    :param out_file_name: name of file where result will be stored
    :return: drawing object
    """
    drawing = svgwrite.Drawing(out_file_name, debug=debug, size=size)
    drawing.viewbox(*view_box)
    return drawing


def polar_to_cartesian(x, y, radius, angle_degrees):
    """
    Function to convert polar coordinates to cartesian
    :param x: x cood
    :param y:
    :param radius:
    :param angle_degrees:
    :return:
    """
    angle_radians = angle_degrees * math.pi / 180.0
    return x + (radius * math.cos(angle_radians)), y + (radius * math.sin(angle_radians))


def describe_arc(x, y, radius, start_angle, end_angle):
    """
    function to draw arcs of different radius and angle
    :param x:
    :param y:
    :param radius:
    :param start_angle:
    :param end_angle:
    :return:
    """
    start = polar_to_cartesian(x, y, radius, end_angle)
    end = polar_to_cartesian(x, y, radius, start_angle)

    large_arc_flag = "0" if end_angle - start_angle <= 180 else "1"

    d = " ".join(
        ["M", str(start[0]), str(start[1]), "A", str(radius), str(radius), "0", large_arc_flag, "0", str(end[0]),
         str(end[1])])
    return d


def add_grid(obj: svgwrite.Drawing, s=10):
    pattern_small_grid = obj.pattern(insert=None, size=(s, s), patternUnits='userSpaceOnUse')
    pattern_small_grid.attribs['id'] = "smallGrid"
    path_small = obj.path(f'M {s} 0 L 0 0 0 {s}', stroke='gray', fill='none', style=f'stroke-width:{0.5}')
    pattern_small_grid.add(path_small)

    pattern_large_grid = obj.pattern(insert=None, size=(s * 10, s * 10), patternUnits='userSpaceOnUse')
    pattern_large_grid.attribs['id'] = "grid"
    path_large = obj.path(f'M {s * 10} 0 L 0 0 0 {s * 10}', stroke='gray', fill='none', style=f'stroke-width:{1}')
    pattern_large_grid.add(path_large)

    rect_large = obj.rect(fill="url(#smallGrid)", size=(s * 10, s * 10))
    pattern_large_grid.add(rect_large)

    obj.defs.add(pattern_small_grid)
    obj.defs.add(pattern_large_grid)

    rect_grid = obj.rect(size=('100%', '100%'), fill="url(#grid)")
    obj.add(rect_grid)


def set_bg_color(obj: svgwrite.Drawing, plant_model, ctx: Context):
    """
    function to set background color for SVG drawing
    :param obj: drawing t oset color on
    :param plant_model: PlantModel proteus object
    :param ctx: model context
    :return: None
    """
    bg_color = fetch_color_from_presentation(plant_model.find('Drawing').find('Presentation'))
    bg_color_rect = obj.rect((0, 0), ('100%', '100%'), fill=bg_color)
    obj.add(bg_color_rect)
