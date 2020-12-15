#!/usr/bin/env python3
################################################################################
"""post_client.py -- demo client script for hepia's LSDS IoT Z-Wave Lab

This script sends POST or GET HTTP requests to a REST server. POST requests
contain parameters in JSON format.

Usage:

    post_client.py [OPTIONS] CLASS COMMAND

See `post_client.py -h` for the details


REST command paths
==================

GET requests
------------

URL path:

    /<class>[/<node_id>]/<command>[/<index>]

where `node_id` and `index` must be specified via explicit CL
options, respectively `-n` and `-i`.


POST requests
-------------

URL path:

    /<class>/<command>

with JSON payload specified via the CL option `-d`.


Examples
========

Dump network topology:

    post_client.py network info


Switch to inclusion mode (20s timeout):

    post_client.py nodes add


Switch to exclusion mode (20s timeout):

    post_client.py nodes remove_node


Get dimmer level for a specific node (given as CL option `-n`):

    post_client.py dimmers get_level -n 5


Set dimmer level for a specific node (notice how the ID is specified in
the JSON payload):

    post_client.py dimmers set_level -d '{"node_id": 5, "value": 50}'


Get value for a generic parameter at index '111' ("Report group 1" time
interval) for node '5':

    python3 post_client.py nodes parameter -n 5 -i 111


Set value for a generic parameter at index '111' for node '5':

    python3 post_client.py nodes set_parameter \
        -d '{"node_id": 5, "value": 480, "index": 111, "size": 4}'


Set value for a generic parameter at index '111' for all sensor nodes:

    python3 post_client.py sensors set_parameter_all \
        -d '{"value": 480, "index": 111, "size": 4}'


Get all measures for a given node

    post_client.py sensors readings -n 2


Print a specfic field from the JSON responseGet all measures for a given node

    post_client.py sensors readings -n 2 -f updateTime


Bugs
====

* At least CLASS and COMMAND must be given to get the script's manual with
  `-m`.

* Setting generic parameter doesn't seem to work properly: (the parameter is
  created if not existing,) it's value stays always at 0.

"""
################################################################################
import requests, argparse, json, simplejson, sys, copy, logging, traceback


################################################################################
# constants

http_headers = {
    'Content-Type' : 'application/json'
}

# cross reference with default node ID, par index and data (where needed)
command_xref = {
    'network'   : {
        'nodes_configuration' : {
            'method' : 'GET',
        },
        'hard_reset' : {
            'method' : 'POST',
            'data'   : {
                'force' : 0,
            }
        },
        'info' : {
            'method' : 'GET',
        },
        'reset' : {
            'method' : 'GET',
        },
        'start' : {
            'method' : 'GET',
        },
        'stop' : {
            'method' : 'GET',
        },
        'nodes' : {
            'method' : 'GET',
        },
        'sensors' : {
            'method' : 'GET',
        },
        'dimmers' : {
            'method' : 'GET',
        },
    },

    'node'     : {
        'add' : {
            'method' : 'GET',
        },
        'location' : {
            'method'    : 'GET',
            'node_id'   : 1,
        },
        'name' : {
            'method'    : 'GET',
            'node_id'   : 1,
        },
        'neighbours' : {
            'method'    : 'GET',
            'node_id'   : 1,
        },
        'list' : {
            'method' : 'GET',
        },
        'parameter' : {
            'method'    : 'GET',
            'node_id'   : 2,
            'index'     : 111, # Report group 1 time interval
        },
        'remove' : {
            'method' : 'GET',
        },
        'set_location' : {
            'method' : 'POST',
            'data'   : {
                'node_id' : '1',
                'value'   : 'A402'
            }
        },
        'set_name' : {
            'method' : 'POST',
            'data'   : {
                'node_id' : '2',
                'value'   : 'my_node'
            }
        },
        'set_parameter' : {
            'method' : 'POST',
            'data'   : {
                'node_id'       : '2',
                'value'         : '480', # seconds
                'index'         : '111', # Report group 1 time interval
                'size'          : '4'
            }
        }
    },
    'dimmer'   : {
        'level' : {
            'method'    : 'GET',
            'node_id'   : 1,
        },
        'set_level' : {
            'method' : 'POST',
            'data'   : {
                'node_id': '5',
                'value': '10'
            }
        }
    },
    'sensor'   : {
        'set_parameter_all' : {
            'method' : 'POST',
            'data'   : {
                'value'       : '480', # seconds
                'index'       : '111', # Report group 1 time interval
                'size'        : '4'
            }
        },
        'readings' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'battery' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'humidity' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'luminance' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'ultraviolet' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'motion' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
        'list' : {
            'method'    : 'GET',
        },
        'temperature' : {
            'method'    : 'GET',
            'node_id'   : 2,
        },
    },
}


################################################################################
# functions

def build_request_path(
        cclass, command, cmnd_s,
        node_id=None,
        pindex=None,
):
    """Build a request path.

    :returns str: a string like '/<class>[/<node_id>]/<command>[/<parameter>]'
                  or None on errors

    Arguments
    +++++++++

    :param str cclass: the resource/object class

    :param str command: the command name

    :param dict cmnd_s: the command spec dict as in `command_xref`

    Keywords arguments
    ++++++++++++++++++

    :param int node_id: the target node to query

    :param int pindex: the parameter index to query

    """
    if 'node_id' in list(cmnd_s.keys()):
        node_id = node_id or cmnd_s['node_id']
    elif node_id:
        logger.error(
            "/{}/{}: unexepected 'node_id' ({}) for this request".format(
                cclass, command, node_id
            )
        )
        return None

    if 'index' in list(cmnd_s.keys()):
        pindex = pindex or cmnd_s['index']
    elif pindex:
        logger.error(
            "/{}/{}: unexepected 'pindex' ({}) for this request".format(
                cclass, command, pindex
            )
        )
        return None

    return '/' + cclass + '/' \
        + (( str(node_id) + '/' ) if node_id != None else '') + command \
        + (( '/' + str(pindex) ) if pindex != None else '')


################################################################################
# main
################################################################################
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s'
)
logger = logging.getLogger('rest_client')

parser = argparse.ArgumentParser(
    description='Demo client for REST-based Z-Wave deployments -- hepia/LSDS Smart-Building',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument(
    '-l, --log-level',
    dest='log_level',
    type=str,
    default='WARNING',
    choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
    help='Logging level'
)

parser.add_argument(
    '-D', '--debug',
    dest='debug',
    action='store_true',
    help='enable debugging facilities'
)

parser.add_argument(
    '-m', '--manual',
    dest='manual',
    action='store_true',
    help='print the full documentation'
)

parser.add_argument(
    '-u', '--server-url',
    dest='server_url',
    type=str,
    default='http://192.168.43.122',
    help='REST server URL'
)

parser.add_argument(
    '-p', '--server-port',
    dest='server_port',
    type=int,
    default=5000,
    help='REST server PORT'
)

parser.add_argument(
    '-f', '--fields',
    dest='fields',
    nargs='*',
    help='List of fields to match in the response (one level only), instead of the whole JSON strucuture'
)

################################################################################
# subcommands
subparsers = parser.add_subparsers(
    title='class',
    dest='subparser_name',
    help='Command/target class: network, node, dimmer, sensor'
)

# @network
parser_network = subparsers.add_parser(
    'network',
    help='Network-related commands',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser_network.add_argument(
    'command',
    type=str,
    choices=(
        'nodes_configuration',
        'hard_reset',
        'info',
        'reset',
        'start',
        'stop',
        'nodes',
        'sensors',
        'dimmers'
    ),
    help='Network commands'
)

parser_network.add_argument(
    '-d', '--data',
    dest='data',
    type=str,
    help='JSON payload string for POST requests'
)

# @node
parser_node = subparsers.add_parser(
    'node',
    help='Node-related commands',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser_node.add_argument(
    'command',
    type=str,
    choices=(
        'add',
        'location',
        'name',
        'neighbours',
        # 'list',
        'parameter',
        'remove',
        'set_location',
        'set_name',
        'set_parameter',
    ),
    help='Commands'
)

parser_node.add_argument(
    '-n', '--node-id',
    dest='node_id',
    type=int,
    help='Node ID'
)

parser_node.add_argument(
    '-i', '--parameter-index',
    dest='index',
    type=int,
    help='Parameter index'
)

parser_node.add_argument(
    '-d', '--data',
    dest='data',
    type=str,
    help='JSON payload string for POST requests'
)


# @sensor
parser_sensor = subparsers.add_parser(
    'sensor',
    help='Sensor-related commands',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser_sensor.add_argument(
    'command',
    type=str,
    choices=(
        'set_parameter_all', # for all sensors
        'readings',
        'battery',
        'humidity',
        'luminance',
        'motion',
        # 'list',
        'temperature',
        'ultraviolet'
    ),
    help='Commands'
)

parser_sensor.add_argument(
    '-n', '--node-id',
    dest='node_id',
    type=int,
    help='Node ID'
)

parser_sensor.add_argument(
    '-d', '--data',
    dest='data',
    type=str,
    help='JSON payload string for POST requests'
)


# @dimmer
parser_dimmer = subparsers.add_parser(
    'dimmer',
    help='Dimmer-related commands',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser_dimmer.add_argument(
    'command',
    type=str,
    choices=(
        'level',
        'set_level'
    ),
    help='Commands'
)

parser_dimmer.add_argument(
    '-n', '--node-id',
    dest='node_id',
    type=int,
    help='Node ID'
)

parser_dimmer.add_argument(
    '-d', '--data',
    dest='data',
    type=str,
    help='JSON payload string for POST requests'
)

################################################################################
args = parser.parse_args()

if args.manual:
    print(__doc__)
    sys.exit(0)

log_level_n = getattr(logging, args.log_level.upper(), None)
if not isinstance(log_level_n, int):
    raise ValueError('Invalid log level: {}'.format(args.log_level))

logger.setLevel(args.log_level)

cclass = args.subparser_name
if not cclass:
    parser.print_usage()
    sys.exit('\nPlease provide a command "class"')

logger.debug('args: {}'.format(args))

command = args.command
data = {}
try:
    data = args.data
    if data:
        try:
            data = json.loads(args.data)
        except Exception as e:
            logger.error("{}: invalid JSON data: {}".format(args.data, e))
            sys.exit(1)
except AttributeError:
    # handled downstream
    pass

cmnd_s = {}
try:
    cmnd_s = command_xref[cclass][command]
except KeyError:
    parser.print_help()
    logger.error("{}: {}: no such command available for this class".format(cclass, command))
    sys.exit(1)

nid = None
try:
    nid = args.node_id
except AttributeError:
    # handled downstream
    pass

pidx = None
try:
    pidx = args.index
except AttributeError:
    # handled downstream
    pass

command_path = build_request_path(
    cclass, command, cmnd_s,
    node_id=nid,
    pindex=pidx
)

if not command_path:
    logger.fatal("Can't build command path")
    sys.exit(1)

method = cmnd_s['method']
if 'data' in list(cmnd_s.keys()):
    data = data or cmnd_s['data']
elif data:
    sys.exit("{}: unexpected data for command path".format(command_path))


logger.info("Sending {} request path: '{}'".format(method, command_path))
if data:
    logger.info("With payload: '{}'".format(data))


base_url = "{}:{}".format(args.server_url, args.server_port)
try:
    req = requests.request(
        method, base_url + command_path,
        headers=http_headers,
        data=json.dumps(data)
    )
except Exception:
    (type, value, trace) = sys.exc_info()
    if args.debug:
        sys.exit("Can't send request: {}\n{}".format(value, traceback.format_exc()))
    else:
        sys.exit("Can't send request: {}: {}".format(type, value))

status = req.status_code
try:
    response = req.json();
    # filter here
    if args.fields:
        try:
            response = { f: response[f] for f in args.fields }
        except KeyError as e:
            logger.warning('{}: no such field name in JSON response'.format(e))

    response = json.dumps(response, sort_keys=True, indent=4)

except (
        json.decoder.JSONDecodeError,
        simplejson.JSONDecodeError
) as e:
    # no data returned
    response = req.text;
    logger.warning('No data returned')

logger.info("Server HTTP response status: {}".format(status))
print((format(response)))

sys.exit(0)
