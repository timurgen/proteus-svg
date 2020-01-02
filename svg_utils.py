import svgwrite


def get_default(out_file_name: str) -> svgwrite.Drawing:
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

    :param out_file_name: name of file where result will be stored
    :return: drawing object
    """
    drawing = svgwrite.Drawing(out_file_name)

    drawing.attribs['overflow'] = 'scroll'
    drawing.defs.add(svgwrite.container.Style())

    default_filter = svgwrite.filters.Filter(('-40%', '-40%'), ('200%', '200%'), id='glow')

    default_filter.feOffset(in_='SourceGraphic', dx=0, dy=0, result='offOut')
    default_filter.feGaussianBlur(in_='offOut', result='blurOut', stdDeviation=2)
    default_filter.feBlend(in_='SourceGraphic', in2='blurOut', mode='normal')

    drawing.defs.add(default_filter)
    return drawing
