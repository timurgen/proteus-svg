import logging
import sys
import os
import lxml.etree as xml

from flask import Flask, request, abort, Response

from proteus_lib.model_context import Context, Unit
from proteus_lib.svg_utils import get_default, add_grid, set_bg_color
from proteus_lib.handlers import process_node
from proteus_lib.proteus_utils import get_model_dimensions_from_plant_model

ROOT_ELEMENT = 'PlantModel'

THREAD_POOL_SIZE = int(os.environ.get('THREAD_POOL_SIZE', 32))
APP = Flask(__name__)

PARSER = xml.XMLParser(remove_comments=True)


@APP.route('/', methods=['POST'])
def process_file():
    debug = bool(request.args.get('debug'))
    grid = request.args.get('grid')

    for file in request.files:
        input_file = xml.parse(request.files[file], PARSER)

        plant_model = input_file.getroot()
        if plant_model.tag != ROOT_ELEMENT:
            abort(400, f'malformed file {file}, {ROOT_ELEMENT} expected at root level')

        pl_info = plant_model.find('PlantInformation')
        m_unit = Unit[pl_info.attrib['Units']]

        # proteus coordinates
        x_min, y_min, x_max, y_max = map(lambda x: x * m_unit.value, get_model_dimensions_from_plant_model(plant_model))

        drawing = get_default(f'{file}.svg', size=(x_max, y_max),
                              view_box=(0, 0, x_max, y_max))
        model_context = Context(drawing=drawing,
                                x_min=x_min, x_max=x_max,
                                y_min=y_min, y_max=y_max,
                                debug=debug,
                                origin=pl_info.attrib['OriginatingSystem'],
                                units=m_unit,
                                shape_catalog=plant_model.find('ShapeCatalogue'))

        set_bg_color(drawing, plant_model)

        if grid is not None:
            add_grid(drawing, int(grid) if grid.isnumeric() else 10)

        process_node(plant_model, drawing, model_context)
        return Response(drawing.tostring(), mimetype='image/svg+xml')


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    port = int(os.environ.get('PORT', '5000'))
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        APP.run(debug=True, host='0.0.0.0', port=port)
    else:
        import cherrypy

        cherrypy.tree.graft(APP, '/')
        cherrypy.config.update({
            'environment': 'production',
            'engine.autoreload_on': True,
            'log.screen': False,
            'server.socket_port': port,
            'server.socket_host': '0.0.0.0',
            'server.thread_pool': THREAD_POOL_SIZE,
            'server.max_request_body_size': 0
        })

        cherrypy.engine.start()
        cherrypy.engine.block()
