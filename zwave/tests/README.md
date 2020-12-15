# Test sheet for the lab evaluation #

Instruction for the demo tests to be performed with your Z-Wave kit.

**Legend:**

* `c$`: prompt of your *client* console/terminal on your workstation
* `s$`: prompt of your *server* console/terminal on your Raspberry Pi


## Environment preparation ##

**N.B.** Log level is set to 'debug' here below.

### Server side ###

Modify the two variables `rbpi_ip` and `srv_path` to suit
your installation:
```shell
s$ rbpi_ip=192.168.1.yx
s$ srv_path=.
s$ alias zwsrv="${srv_path}/flask-main.py -H ${rbpi_ip} -l debug"
```

Then run the server:
```shell
s$ zwsrv
```

### Client side ###

Modify the two variables `rbpi_ip` (must be the same as
above) and `cli_path` to suit your installation:
```shell
c$ rbpi_ip=192.168.1.yx
c$ cli_path=.
c$ alias zwcli="${cli_path}/post_client.py -u http://${rbpi_ip} -l debug"
```

## Reset your Z-Wave network ##

1. Connect the multisensor and switch off the dimmer.

1. Remove any active node and hard reset (it might take several seconds) the
   controller via API commands:
   ```shell
   c$ zwcli node remove
   c$ zwcli node remove
   c$ ...
   c$ zwcli network nodes
   {
       "1": "ZME_UZB1 USB Stick"
   }
   c$ zwcli network hard_reset
   [
       true,
       "OK"
   ]
   ```
   **N.B.** If the `hard_reset` hangs (no reply after a couple minutes): kill
   the server (`s$ pkill python3`), disconnect and reconnect the UZB stick.

1. Shut down the server with `CTRL+C`, remove OZW artifacts, then restart the
   server:
   ```shell
   s$ zsrv
   ...
   ^C
   s$ rm -rf ~/tmp/OZW
   s$ zsrv
   ```

## Tests ##

### Network and nodes ###

1. Test inclusion/exclusion timeout. Do not touch any device; the prompt must
   return after 20".
   ```shell
   c$ zwcli node add
   WARNING  No data returned
   InclusionError -- Timeout. Inclusion cancelled.
   c$ zwcli node remove
   WARNING  No data returned
   ExclusionError -- Timeout. Exclusion cancelled.
   ```

1. Add a sensor and a dimmer
   ```shell
   c$ zwcli node add
   ...
   c$ zwcli node add
   ...
   c$ zwcli network nodes
   {
       "1": "ZME_UZB1 USB Stick",
       "2": "MultiSensor 6",
       "3": "Unknown: type=4c42, id=3134"
   }
   c$ zwcli network info
   ...
   ```

1. Probe and set a node's configuration parameter (report 1 interval)
   ```shell
   c$ zwcli node parameter -n 255 -i 111
   WARNING  No data returned
   QueryFail -- No such node
   c$ zwcli node parameter -n 3 -i 111
   null                # OK, not a sensor
   c$ zwcli node parameter -n 2 -i 111
   3600
   c$ zwcli node set_parameter -d '{"node_id": 2, "value": 480, "index": 111, "size": 4}'
   [
       true,
       "OK"
   ]
   c$ zwcli node parameter -n 2 -i 111
   480
   ```

1. Probe and set a node's info field
   ```shell
   c$ zwcli node location -n 3
   ""
   c$ zwcli node set_location -d '{"node_id": 3, "value": "lab"}'
   [
       "",             # previous value
       "OK"
   ]
   c$ zwcli node location -n 3
   "lab"
   ```

1. List a node's neighbours
   ```shell
   c$ zwcli node neighbours -n 3
   [
       1,
       2
   ]
   ```

### Sensor ###

1. Get all of a sensor's readings
   ```shell
   c$ zwcli sensor readings -n 2
   {
       "battery": 100,
       "burglar": 8,
       "controller": "Pi lab1",
       "humidity": 28.0,
       "location": "",
       "luminance": 301.0,
       "motion": false,
       "sensor ID": 2,
       "temperature": 27.100000381469727,
       "ultraviolet": 0.0,
       "updateTime": 1604489422
   }
   ```

1. Get a sensor's specific reading
   ```shell
   c$ zwcli sensor humidity -n 2
   {
       "controller": "Pi lab1",
       "location": "",
       "sensor": 2,
       "type": "humidity",
       "updateTime": 1604489422,
       "value": 28.0
   }
   ```

1. Get a sensor's battery level
   ```shell
   c$ zwcli sensor battery -n 2
   {
       "controller": "Pi lab1",
       "location": "",
       "sensor": 2,
       "type": "battery",
       "updateTime": 1604494550,
       "value": 100
   }
   ```

### Dimmer ###

1. Get a dimmer's level
   ```shell
   c$ zwcli dimmer level -n 2
   WARNING  No data returned
   QueryFail -- Not a dimmer
   c$ zwcli dimmer level -n 3
   {
       "controller": "Pi lab1",
       "dimmer": 3,
       "location": "lab",
       "type": "level",
       "updateTime": 1604489280,
       "value": 99
   }
   ```

1. Set a dimmer's level
   ```shell
   c$ zwcli dimmer set_level -d '{"node_id": 3, "value": 50}'
   99                               # previous value
   c$ zwcli dimmer level -n 3
   {
       "controller": "Pi lab1",
       "dimmer": 3,
       "location": "lab",
       "type": "level",
       "updateTime": 1604490377,
       "value": 50
   }
   ```

### Clean-up ###

Remove the nodes and reset the controller

```shell
c$ zwcli node remove
...
c$ zwcli node remove
...
c$ zwcli network hard_reset
[
    true,
    "OK"
]
c$ zwcli network info
{
    "1": {
        "Is Ready": true,
        "Neighbours": [],
        "Node ID": "1",
        "Node location": "A402",
        "Node name": "",
        "Node type": "Static PC Controller",
        "Product name": "ZME_UZB1 USB Stick",
        "Query Stage": "Complete",
        "Query Stage (%)": 100
    },
    "Network Home ID": "0xee9e440e"
}
```

## Bugs ##

* A hard reset may hang: a reboot might be needed.
