#! /usr/bin/env python3
# #-*- coding: utf-8; tab-width: 4 -*-
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
import requests
import json
import threading
import subprocess
from notification import * 

file_path = os.path.dirname(__file__)
sys.path.insert(0, file_path)

from flask import Flask, jsonify, Response, request
from flask.logging import default_handler

my_name = re.split('\.py', __file__)[0]
app = Flask(
    __name__,
    # just for serving apidoc static files
    static_folder=os.path.abspath("doc/"),
    static_url_path=''
)

zwave_server_address = None

knx_gateway = None
zwave_gateway = None

_rooms_devices = {
    "31126" : {
        "radiators" : 
            {
                "4/1",
                "4/2"
            },
        "blinds" :
            {
                "4/1",
                "4/2"
            }

    },
    "19547" : {
        "radiators" : 
            {
                "4/10",
                "4/11"
            },
        "blinds" :
            {
                "4/10",
                "4/11"
            }

    }
}

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

@app.route('/light', methods=['POST'], strict_slashes=False)
def set_light_level():
    room, value = get_param_from_post_request(request)
    if((room != None) & (value != None)):
        try:
            myJson = {"room_id": room, "value" : value}
            r = requests.post("http://" + str(zwave_gateway) + "/room/light", json={'room_id': room, 'value': value})
            return True
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)


@app.route('/radiator', methods=['POST'], strict_slashes=False)
def set_radiator_level():
    room, value = get_param_from_post_request(request)
    if((room != None) & (value != None)):
        try:            
            radiators = _rooms_devices[room]["radiators"]
            for radiator in radiators : 
                command = "./knx_client.py -i " + knx_gateway + " valve set '" + radiator + "' " + str(value)
                os.system(command)
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)

@app.route('/store', methods=['POST'], strict_slashes=False)
def set_store_level():
    room, value = get_param_from_post_request(request)
    if((room != None) & (value != None)):
        try:            
            blinds = _rooms_devices[room]["blinds"]
            for blind in blinds :
                command = "./knx_client.py -i " + knx_gateway + " blind set '" + blind + "' " + str(value)
                os.system(command)
        except RuntimeError as e:
            return ("QueryFail -- {}".format(e), 400)
        except OverflowError as e:
            return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)

@app.route('/room/<room>', strict_slashes=False)
def get_room_values(room):
    values = []
    try:            
        blinds = _rooms_devices[room]["blinds"]
        for blind in blinds :
            command = "./knx_client.py -i " + knx_gateway + " blind get '" + blind + "' " 
            try:
                output = subprocess.check_output(command, shell=True)
                output = output.decode("UTF-8")
                values.append(output[output.find("(")+1:output.find(")")])
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        valves = _rooms_devices[room]["radiators"]
        for valve in valves :
            command = "./knx_client.py -i " + knx_gateway + " valve get '" + valve + "' " 
            try:
                output = subprocess.check_output(command, shell=True)
                output = output.decode("UTF-8")
                values.append(output[output.find("(")+1:output.find(")")])
            except subprocess.CalledProcessError as e:
                raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        return jsonify(values)

    except RuntimeError as e:
        return ("QueryFail -- {}".format(e), 400)
    except OverflowError as e:
        return ("WrongInput -- {}".format(e), 400)

    return ("WrongInput -- Wrong input parameter(s) provided", 400)

def get_param_from_post_request(request):
    content = request.get_json()
    if all(
            item in list(content.keys()) for item in [
                'room', 'data'
            ]
    ):
        return str(content['room']), int(content['data'])

    else:
        return None, None

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
        '--knx-gateway',
        type=str,
        dest='knx_gateway',
        help='KNX Gateway IP address'
    )
    
    parser.add_argument(
        '--zwave-gateway',
        type=str,
        dest='zwave_gateway',
        help='Z-Wave Gateway IP address'
    )

    parser.add_argument(
        '-p, --port',
        dest='port',
        type=int,
        default=5001,
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

    knx_gateway = args.knx_gateway
    zwave_gateway = args.zwave_gateway

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
        zwave_server_address = "http://192.168.0.194:5000"
        device_method_thread = threading.Thread(target=notify, args=(zwave_server_address,knx_gateway,))
        device_method_thread.daemon = True
        device_method_thread.start()
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
        print("Bye, bye!")
