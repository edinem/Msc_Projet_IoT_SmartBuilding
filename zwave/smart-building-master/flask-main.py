#! /usr/bin/env python3
#-*- coding: utf-8; tab-width: 4 -*-
################################################################################
"""flask_main.py -- a Flask-based server for hepia's LSDS IoT Z-Wave Lab
(frontend)

Documentation is written in `apidoc <http://www.python.org/>`_. You should
already have a copy in `doc/index.html`

To-do
=====

Next milestones:

[ ] Unify get/set route into a single parametric one dispatched over GET or POST.

Bugs
====

None known, many unknown ;-)
"""
################################################################################
import sys, time, logging, configpi, os, argparse, re

file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)

from flask import Flask, jsonify, Response, request
from flask.logging import default_handler
from backend import *
import threading

my_name = re.split('\.py', __file__)[0]
app = Flask(
    __name__,
    # just for serving apidoc static files
    static_folder=os.path.abspath("doc/"),
    static_url_path=''
)

backend = None


################################################################################

# @app.before_request
def clear_trailing():
    """Remove all repeated '/' -- we don't use schemeless URLs!? BTW, this
    should be fixed with werkzwug v1.x. See
<comnfi# app = Flask(__name__, static_url_path='')
https://github.com/pallets/werkzeug/issues/491> and
<https://stackoverflow.com/questions/40365390/trailing-slash-in-flask-route>
    """
    rp = request.path
    if re.match('//+', rp):
        return redirect(re.sub('/+', '/', rp))


################################################################################
# Global APIdoc defines
################################################################################
"""
@apiDefine          SuccessOK
@apiSuccess         {Object}    ...     JSON array
@apiSuccessExample  {Object}            Success response
    [True, 'OK']
"""

"""
@apiDefine          SuccessOKOldValue
@apiSuccess         {Object}    ...     JSON array
@apiSuccessExample  {Object}            Success response
    [<old-value>, 'OK']
"""

"""
@apiDefine          SuccessJSONArray
@apiSuccess         {Object}    ... JSON associative array. See example below.
"""

"""
@apiDefine          SuccessJSONArrayProduct
@apiSuccess         {Object}    ... JSON associative array keyed by nodes' IDs with
                                    values as nodes' "product names"
"""

"""
@apiDefine          ErrorNoSuchNode
@apiError           QueryFail     Reason: "No such node".
"""

"""
@apiDefine          ErrorQuerySensor
@apiError QueryFail     The query failed. Possible reasons:
                            "No such node",
                            "Not ready",
                            "Not a sensor".
"""

"""
@apiDefine          ErrorQueryDimmer
@apiError QueryFail     The query failed. Possible reasons:
                            "No such node",
                            "Not ready",
                            "Not a dimmer".
"""
################################################################################
# @index page
################################################################################
@app.route('/', strict_slashes=False)
def index():
    """Display API documentation
    """
    return app.send_static_file("index.html")


################################################################################
# @network
################################################################################
"""
@api        {get}   /network/info   Overview
@apiName    get_network_info
@apiGroup   Network

@apiDescription     Gets an overview of Z-Wave network in a JSON format

@apiSuccess         {Object}    ... JSON associative array indexed by node
                                    IDs. See example below.

@apiSuccessExample  {OBJECT} Success response
{
    "1": {
        "Is Ready": true,
        "Neighbours": [
            2,
            3
        ],
        "Node ID": "1",
        "Node location": "",
        "Node name": "",
        "Node type": "Static PC Controller",
        "Product name": "ZME_UZB1 USB Stick",
        "Query Stage": "Complete",
        "Query Stage (%)": 100       # readiness level: onnce at 100%, the
                                     # node is ready to be used.
    },
    "2": {
        "Is Ready": true,
        "Neighbours": [
            1,
            3
        ],
        "Node ID": "2",
        "Node location": "",
        "Node name": "",
        "Node type": "Home Security Sensor",
        "Product name": "MultiSensor 6",
        "Query Stage": "Complete",
        "Query Stage (%)": 100
    },
    "3": {
        "Is Ready": true,
        "Neighbours": [
            1,
            2
        ],
        "Node ID": "3",
        "Node location": "",
        "Node name": "",
        "Node type": "Light Dimmer Switch",
        "Product name": "Unknown: type=4c42, id=3134",
        "Query Stage": "Complete",
        "Query Stage (%)": 100
    },
    "Network Home ID": "0xd6297cb6"
}
"""
@app.route('/network/info', strict_slashes=False)
def network_info():
    app.logger.debug('@/network/info')
    return jsonify(backend.network_info())


################################################################################
"""
@api        {get}   /network/start  Start
@apiName    network_start
@apiGroup   Network

@apiDescription     Starts the OZW controller and software representation
                    of the network

@apiUse     SuccessOK

@apiError           {Object}    ...     JSON array
@apiErrorExample    {Object}            Error response
    [False, 'System already started. Skipping...']
"""
@app.route('/network/start', strict_slashes=False)
def start():
    return jsonify(backend.start())


################################################################################
"""
@api        {get}   /network/stop   Stop
@apiName    network_stop
@apiGroup   Network

@apiDescription     Stops the OZW software representation of the
        network. Warning! This is broken on some platforms, see Bug
        <https://github.com/OpenZWave/python-openzwave/issues/202>

@apiUse     SuccessOK

@apiError           {Object}    ...     JSON array
@apiErrorExample    {Object}            Error response (reason unknown)
    [False, '[reason]']
"""
@app.route('/network/stop', strict_slashes=False)
def stop():
    result = backend.stop()
    time.sleep(2)
    return jsonify(result)


################################################################################
"""
@api        {post}  /network/hard_reset Hard Reset
@apiName    network_hard_reset
@apiGroup   Network

@apiDescription     Hard-resets the network's controller. You shouldn't call this
        method before excluding (removing) all connected nodes, but you can
        force to do so at your own risk.

@apiParam   {Bool}  force=False Must be set to True to force reset of a network
                                with included nodes.

@apiUse     SuccessOK

@apiError   NetworkHasNodes     A reset was attempted on a network with nodes while
        <code>force=False</code>.
"""
@app.route(
    '/network/hard_reset', methods=['POST'], strict_slashes=False
)
def hard_reset():
    # force = request.args.get('force', False)
    content = request.get_json()
    force = bool(content.pop('force', None))
    if content:
        app.logger.warning("hard_reset: extra parameters found: {}".format(content))

    try:
        return jsonify(backend.hard_reset(force))
    except RuntimeError as e:
        return ("NetworkHasNodes -- {}".format(e), 400)


################################################################################
"""
@api        {get}   /network/reset  Reset
@apiName    network_reset
@apiGroup   Network

@apiDescription Soft-resets the network's controller. Warning! This will
        power-cycle the controller: the associated device file might
        change. The network will also be restarted.

@apiUse     SuccessOK
"""
@app.route('/network/reset', strict_slashes=False)
def reset():
    res = backend.soft_reset()
    if res[0]:
        res = backend.stop()
        if res[0]:
            res = backend.start()

    return jsonify(res)


################################################################################
"""
@api        {get}   /network/nodes_configuration Configuration
@apiName    get_nodes_configuration
@apiGroup   Network

@apiDescription Gets the list of configuration parameters for all nodes in a
        JSON format.

@apiSuccess {Object} ...  JSON  Associative array keyed by node's IDs, with an
    item for any known node in the network. For a given node type, each
    parameter is univocally identified by its "index".

@apiExample     The following table gives some examples of parameters for an Aeotec MultiSensor 6:
    index  label                    note
    -----------------------------------------------------------------------
        4  "Enable Motion Sensor"   Motion sensor's sensitivity level
      101  "Group 1 Reports"        Which report are to be sent in Report
                                    Group 1 -- set 241 to send all.
      111  "Group 1 Interval"       Seconds between two consecutive Group1
                                    measurements

@apiSuccessExample {Object} Success response
{
    "Network Home ID": "0xe221b13f",
    "2": {
        "72057594081706020": {
            "command_class": 112,
            "data": "No",
            "data_items": [
                "No",
                "Yes"
            ],
            "genre": "Config",
            "index": 2,
            "is_read_only": false,
            "is_write_only": false,
            "label": "Wake up 10 minutes on Power On",
            "node_id": 2,
            "type": "List",
            "units": "",
            "value_id": 72057594081706020
        },
    },
    ...
}
"""
@app.route('/network/nodes_configuration', strict_slashes=False)
def get_nodes_configuration():
    return jsonify(backend.get_nodes_configuration())


################################################################################
"""
@api        {get}   /network/nodes  Nodes
@apiName    get_nodes_list
@apiGroup   Network

@apiDescription Get a list of all the nodes in the network.

@apiUse     SuccessJSONArrayProduct

@apiSuccessExample {Object} Success response
{
  "1": "Z-Stick Gen5",
  "2": "MultiSensor 6",
  "3": "[not ready]"
}
"""
@app.route('/network/nodes', strict_slashes=False)
def nodes():
    return jsonify(backend.get_nodes_list())


################################################################################
"""
@api        {get}   /network/sensors    Sensors
@apiName    get_sensors_list
@apiGroup   Network

@apiDescription     Get a lists of all sensors nodes in the network.

@apiUse     SuccessJSONArrayProduct

@apiSuccessExample {Object} Success response
{
  "2": "MultiSensor 6",
  "3": "[not ready]"
}
"""
@app.route('/network/sensors', strict_slashes=False)
def get_sensors_list():
    return jsonify(backend.get_sensors_list())


################################################################################
"""
@api        {get}   /network/dimmers    Dimmers
@apiName    get_dimmers_list
@apiGroup   Network

@apiDescription Get a lists all dimmers nodes in the network

@apiUse     SuccessJSONArrayProduct

@apiSuccessExample {Object} Success response
{
  "2": "Unknown: type=4c42, id=3134",
  "3": "..."
}
"""
@app.route('/network/dimmers', strict_slashes=False)
def get_dimmers_list():
    return jsonify(backend.get_dimmers_list())


################################################################################
# @node
################################################################################
"""
@api            {get}   /node/add Add
@apiName                add_node
@apiGroup               Node

@apiDescription Adds a (non-controller) node to the network by switching the
    controller into "inclusion" mode for a configurable number of
    seconds. Physical action is required on the node device to be added.

@apiSuccess {Object}    ... The newly added node's full configuration structure.

@apiSuccessExample {Object} Success response
{
  {
    "capabilities": {
        "beaming": 0,
        "listening": 0,
        "routing": 0,
        "zwave_plus": 0
    },
    "groups": {
        "1": {
            "label": "Group 1"
        }
    },
    "location": "",
    "name": "",
    "neighbors": {},
    "node_id": 3,
    "product_name": "Unknown: type=4c42, id=3134",
    "product_type": "0x4c42",
    "values": {
        "72057594093076481": {
            "data": 0,
            "genre": "User",
            "label": "Level",
            "node_id": 3,
            "units": "",
            "value_id": 72057594093076481
        },
    ...
}

@apiError InclusionError The reason is specified in the message:
        "Network not started",
        "Timeout. Inclusion cancelled",
        "Unknown error".
"""
@app.route('/node/add', methods=['GET'], strict_slashes=False)
def add_node():
    node = None
    try:
        node = backend.add_node()
    except RuntimeError as e:
        return ("InclusionError -- {}".format(e), 400)

    return jsonify(node)


################################################################################
"""
@api            {get}   /node/remove Remove
@apiName                remove_node
@apiGroup               Node

@apiDescription Removes a (non-controller) node to the network by switching the
    controller into "exclusion" mode for a configurable number of
    seconds. Physical action is required on the node device to be added.

@apiSuccess {obj} ... The removed node

@apiError InclusionError The reason is specified in the message:
        "Network not started",
        "Timeout. Exclusion cancelled",
        "Unknown error".
"""

@app.route('/node/remove', methods=['GET'], strict_slashes=False)
def remove_node():
    try:
        node = backend.remove_node()
    except RuntimeError as e:
        return ("ExclusionError -- {}".format(e), 400)

    return jsonify(node)


################################################################################
"""
@api            {get}   /node/<node_id>/parameter/<index> Parameter
@apiName        get_parameter
@apiGroup       Node

@apiDescription Gets the value of a node's configuration parameter

@apiParam {Number} node_id Node's ID
@apiParam {Number} index Parameter's index

@apiSuccess {Number/String} ... The parameter's value

@apiError QueryFail     The query failed. Possible reasons:
                            "No such node",
                            "Not ready".

@apiError WrongInput    Index overflow: "Value too large to convert to uint8_t" .
"""
@app.route('/node/<int:node>/parameter/<int:index>', strict_slashes=False)
def get_parameter(node, index):
    try:
        return jsonify(backend.get_node_parameter(node, index))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)
    except OverflowError as e:
        return ("WrongInput -- {}".format(e), 400)


################################################################################
"""
@api            {post}  /node/set_parameter Set parameter
@apiName                set_parameter
@apiGroup               Node

@apiDescription Sets the value of a given node's configuration parameter

@apiParam {Number}        node_id   Nodes's ID
@apiParam {Number}        index     Parameter's index
@apiParam {Number/String} value     Parameter's value
@apiParam {Number}        size      Parameter's size

@apiParamExample {Object} Request-Example :
{
    'node_id' : '4',
    'index' : '101',
    'value' : '227',
    'size' : '4'
}

@apiUse     SuccessOK

@apiError WrongInput    Reasons:
                            "Wrong input parameter(s) were provided",
                            "Value too large to convert to uint8_t" (overflow
                            in any of `index`, `size`, `value`).

@apiError QueryFail     The query failed. Possible reasons:
                            "Command failed",
                            "No such node",
                            "Not ready".
"""
@app.route('/node/set_parameter', methods=['POST'], strict_slashes=False)
def set_parameter():
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'node_id', 'index', 'value', 'size'
            ]
    ):
        node = int(content['node_id'])
        pindex = int(content['index'])
        value = int(content['value'])
        size = int(content['size'])
        try:
            if backend.set_node_parameter(node, pindex, value, size):
                return jsonify((True, 'OK'))
            else:
                # should never happen
                return ("QueryFail -- Command failed".format(e), 400)
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


################################################################################
"""
@api            {post}  /node/set_location Set location
@apiName                set_location
@apiGroup               Node

@apiDescription Set a node's "location" string

@apiParam {Number} node_id  Nodes's ID
@apiParam {String} value    The new location value

@apiParamExample {Object} Request example
    {
        "node_id" : 4,
        "value" : "kitchen"
    }

@apiUse     SuccessOKOldValue

@apiError   WrongInput    Reasons:
                            "Wrong input parameter(s) were provided",
                            "Argument 'location' has incorrect type (expected str, got int).

@apiUse     ErrorNoSuchNode
"""
@app.route('/node/set_location', methods=['POST'], strict_slashes=False)
def set_node_location():
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'node_id', 'value'
            ]
    ):
        node = int(content['node_id'])
        value = content['value']

        try:
            return jsonify((backend.set_node_location(node, value), 'OK'))
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except TypeError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


################################################################################
"""
@api            {post}  /node/set_name Set name
@apiName                set_name
@apiGroup               Node

@apiDescription Sets the name string of a given node

@apiParam {Number} node_id Nodes's ID
@apiParam {String} value new name value

@apiParamExample {Object} Request-Example :
    {
        'node_id' : '4',
        'value' : 'A401-multisensor'
    }

@apiUse     SuccessOKOldValue

@apiError   WrongInput    Reasons:
                            "Wrong input parameter(s) were provided",
                            "Argument 'location' has incorrect type (expected str, got int).

@apiUse     ErrorNoSuchNode
"""
@app.route('/node/set_name', methods=['POST'], strict_slashes=False)
def set_node_name():
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'node_id', 'value'
            ]
    ):
        node = int(content['node_id'])
        value = content['value']

        try:
            return jsonify((backend.set_node_name(node, value), 'OK'))
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except TypeError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


################################################################################
"""
@api            {get}   /node/<node_id>/location Location
@apiName                get_location
@apiGroup               Node

@apiDescription Retreve the location string of a given node

@apiParam {Number} node_id Node's ID

@apiUse     SuccessOKOldValue
@apiUse     ErrorNoSuchNode
"""
@app.route('/node/<int:node_id>/location', strict_slashes=False)
def get_node_location(node_id):
    try:
        return jsonify(backend.get_node_location(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /node/<node_id>/name Name
@apiName                get_name
@apiGroup               Node

@apiDescription Gets name of a given node

@apiParam {Number} node_id Node' ID

@apiUse     SuccessOKOldValue
@apiUse     ErrorNoSuchNode
"""
@app.route('/node/<int:node_id>/name', strict_slashes=False)
def get_node_name(node_id):
    try:
        return jsonify(backend.get_node_name(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /node/<node_id>/neighbours Neighbours
@apiName                get_neighbours
@apiGroup               Node

@apiDescription Gets a list of a node's neighbours

@apiParam {Number} node_id Node's ID

@apiSuccess         {Object}    ...     JSON array(Number, ...)
@apiSuccessExample  {Object}            Success response
    [2, 3]

@apiUse     ErrorNoSuchNode
"""
@app.route('/node/<int:node_id>/neighbours', strict_slashes=False)
def get_neighbours_list(node_id):
    try:
        return jsonify(backend.get_neighbours_list(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
# @sensors
################################################################################
"""
@api            {post}  /sensor/set_parameter_all Set parameter for all
@apiName        set_parameter_all
@apiGroup       Sensor

@apiDescription Set a configuration parameter for all sensor nodes in the network.

@apiParam {Number} index    Parameter's index
@apiParam {Number} value    Parameter's new value
@apiParam {Number} size     Parameter's size

@apiParamExample {Object} Request Example
{
    'index' : '101',
    'value' : '227',
    'size' : '4'
}

@apiSuccess         {Object}    ...     JSON associative array keyed by nodes' IDs
@apiSuccessExample  {Object}            Success response
{
  "2": [true, "OK"],
  "3": [false, "Not ready"],
  "4": [false, "Command failed"],
  ...
}

@apiError WrongInput    Reasons:
                            "Wrong input parameter(s) were provided".

@apiError QueryFail     The query failed. Possible reasons:
                            "Network not started".
"""
@app.route('/sensor/set_parameter_all', methods=['POST'], strict_slashes=False)
def set_parameter_all():
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'index', 'value', 'size'
            ]
    ):
        pindex = int(content['index'])
        value = int(content['value'])
        size = int(content['size'])
        try:
            return jsonify(backend.set_sensors_parameter(pindex, value, size))
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/readings Readings
@apiName                readings
@apiGroup               Sensor

@apiDescription Gets all measureament readings of a sensor, in a JSON format

@apiParam {Number} node_id Sensor's ID

@apiUse    SuccessJSONArray
@apiSuccessExample {Object} Success response
{
  "battery": 100,
  "controller": "Pi lab1",
  "humidity": 22,
  "location": "Room A401",
  "luminance": 60,
  "motion": false,
  "sensor": 2,
  "temperature": 30.0,
  "updateTime": 1454682568
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/readings', strict_slashes=False)
def readings(node_id):
    try:
        return jsonify(backend.get_sensor_readings(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/battery Battery
@apiName                battery
@apiGroup               Sensor

@apiDescription Gets the battery level of a sensor, in a JSON format.

@apiParam {Number} node_id Sensor's ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "battery",
  "updateTime": 1454684168,
  "value": 100
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/battery', strict_slashes=False)
def battery(node_id):
    try:
        return jsonify(backend.get_sensor_battery(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/temperature Temperature
@apiName                temperature
@apiGroup               Sensor

@apiDescription Gets the temperature reading of a sensor in a JSON format.

@apiParam {Number} node_id Sensor's ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "temperature",
  "updateTime": 1454682568,
  "value": 30.4
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node>/temperature', strict_slashes=False)
def temperature(node):
    try:
        return jsonify(backend.get_sensor_temperature(node))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/humidity Humidity
@apiName                humidity
@apiGroup               Sensor

@apiDescription Gets the humidity reading of a sensor in a JSON format

@apiParam {Number} node_id Sensor's ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "humidity",
  "updateTime": 1454682996,
  "value": 21
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/humidity', strict_slashes=False)
def humidity(node_id):
    try:
        return jsonify(backend.get_sensor_humidity(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/luminance Luminance
@apiName                luminance
@apiGroup               Sensor

@apiDescription Gets the luminance reading of a sensor in a JSON format

@apiParam {Number} node_id Sensor's unique ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "luminance",
  "updateTime": 1454682996,
  "value": 49
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/luminance', strict_slashes=False)
def luminance(node_id):
    try:
        return jsonify(backend.get_sensor_luminance(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/motion Motion (burglar)
@apiName                motion
@apiGroup               Sensor

@apiDescription Gets the motion (burglar) reading of a sensor in a JSON format.

@apiParam {Number} node_id Sensor's unique ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "sensor",
  "updateTime": 1454682996,
  "value": true
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/motion', strict_slashes=False)
def motion(node_id):
    try:
        return jsonify(backend.get_sensor_motion(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {get}   /sensor/<node_id>/ultraviolet Ultraviolet
@apiName                ultraviolet
@apiGroup               Sensor

@apiDescription Gets the ultraviolet reading of a sensor in a JSON format.

@apiParam {Number} node_id Sensor's unique ID.

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "sensor": 2,
  "type": "ultraviolet",
  "updateTime": 1454682996,
  "value": 0.2
}

@apiUse     ErrorQuerySensor
"""
@app.route('/sensor/<int:node_id>/ultraviolet', strict_slashes=False)
def ultraviolet(node_id):
    try:
        return jsonify(backend.get_sensor_ultraviolet(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
# @dimmers
################################################################################
"""
@api            {get}   /dimmer/<node_id>/level Level
@apiName                level
@apiGroup               Dimmer

@apiDescription Gets the level of a dimmer in a JSON format

@apiParam {Number} node_id Dimmer's ID

@apiUse    SuccessJSONArray

@apiSuccessExample {Object} Success response
{
  "controller": "Pi lab1",
  "location": "Room A401",
  "dimmer": 4,
  "type": "level",
  "updateTime": 1454682996,
  "value": 50
}

@apiUse     ErrorQueryDimmer
"""

@app.route('/dimmer/<int:node_id>/level', strict_slashes=False)
def level(node_id):
    try:
        return jsonify(backend.get_dimmer_level(node_id))
    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)


################################################################################
"""
@api            {post}  /dimmer/set_level Set level
@apiName                set_dimmer_level
@apiGroup               Dimmer

@apiDescription Set the level of a dimmer node

@apiParam {Number} node_id Dimmer's ID
@apiParam {Number} value new level value in [0, 99]

@apiParamExample {Object} Request example
    {
        'node_id' : '4',
        'value' : '50'
    }

@apiUse     SuccessOKOldValue

@apiError   WrongInput    Reasons:
                            "Wrong input parameter(s) were provided",
                            "Argument 'location' has incorrect type (expected int, got str).

@apiUse     ErrorQueryDimmer
"""
@app.route('/dimmer/set_level', methods=['POST'], strict_slashes=False)
def set_dimmer_level():
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'node_id', 'value'
            ]
    ):
        node = int(content['node_id'])
        value = int(content['value'])
        try:
            return jsonify(backend.set_dimmer_level(node, value))
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


@app.route('/room/light', methods=['POST'], strict_slashes=False)
def set_dimmer_level_by_room():
    content = request.get_json()
    print(content)
    if all(
            item in list(content.keys()) for item in [
                'room_id', 'value'
            ]
    ):
        roomid = str(content['room_id'])
        value = int(content['value'])
        try:
            return jsonify(backend.set_dimmers_by_room(roomid, value))
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)

#################################################################
#################################################################

if __name__ == '__main__':

    if not my_name:
        raise RuntimeError("my_name not set")

    parser = argparse.ArgumentParser(
        description='Smart Building RESTful server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '-C, --ozw-config-path',
        dest='ozw_config_path',
        type=str,
        default='/etc/openzwave/',
        help='OZW configuration path -- see your backend lib installation'
    )

    parser.add_argument(
        '-U, --user-path',
        dest='user_path',
        type=str,
        default='~/tmp/OZW/',
        help='User path -- where all artifacts such as logs, etc., are put'
    )

    parser.add_argument(
        '-H, --host-name',
        type=str,
        dest='host_name',
        default='localhost',
        help='Our host-name or IP address'
    )

    parser.add_argument(
        '-p, --port',
        dest='port',
        type=int,
        default=5000,
        help='Our listening port'
    )

    parser.add_argument(
        '-l, --log-level',
        dest='log_level',
        type=str,
        default='warning',
        choices=('debug', 'info', 'warning', 'error', 'critical'),
        help='Logging level. On "debug" flask will auto-reload on file changes'
    )

    parser.add_argument(
        '-m', '--manual',
        dest='manual',
        action='store_true',
        help='print the full documentation'
    )

    parser.add_argument(
        '-R', '--reload',
        dest='reload',
        action='store_true',
        help='switch flask auto-reload on. Only effective when "log-level=debug".' +
        ' Beware of Bug <https://github.com/pallets/werkzeug/issues/1333>. Avoid!'
    )

    args = parser.parse_args()
    if args.manual:
        print(__doc__)
        sys.exit(0)

    log_level_n = getattr(logging, args.log_level.upper(), None)
    if not isinstance(log_level_n, int):
        raise ValueError('Invalid log level: {}'.format(args.log_level))


    # we put all artifacts here (frontend, backend, OZW libs...)
    user_path = os.path.expanduser(
            os.path.expandvars(
                args.user_path
            )
        )
    try:
        os.makedirs(user_path, exist_ok=True)
    except Exception as e:
        sys.exit("Can't create user_path: {}".format(e))

    fh = logging.FileHandler("{}/{}.log".format(user_path, my_name), mode='w')
    fh.setLevel(log_level_n)
    fh.setFormatter(
        logging.Formatter(
            configpi.log_format_dbg if log_level_n <= logging.DEBUG else configpi.log_format
        )
    )

    app.logger.setLevel(log_level_n)
    app.logger.removeHandler(default_handler)
    app.logger.addHandler(fh)

    print("User path is '{}'".format(user_path))

    try:
        backend = Backend_with_dimmers_and_sensors(
            ozw_config_path=args.ozw_config_path,
            ozw_user_path=user_path,
            log_level=log_level_n
        )
        try:
            backend.start()
            pass
        except Exception as e:
            sys.exit(e)
        #device_method_thread = threading.Thread(target=notify, args=(backend,))
        #device_method_thread.daemon = True
        #device_method_thread.start()

        app.run(
            debug=True if log_level_n == logging.DEBUG else False,
            host=args.host_name,
            port=args.port,
            threaded=True,
            # beware: reloading doesn't call a backend.stop(), things may
            # break...
            use_reloader=True if args.reload and log_level_n == logging.DEBUG else False
        )

    except KeyboardInterrupt:
        backend.stop()
        print("Bye, bye!")
