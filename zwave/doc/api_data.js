define({ "api": [
  {
    "type": "get",
    "url": "/dimmer/<node_id>/level",
    "title": "Level",
    "name": "level",
    "group": "Dimmer",
    "description": "<p>Gets the level of a dimmer in a JSON format</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Dimmer's ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"dimmer\": 4,\n  \"type\": \"level\",\n  \"updateTime\": 1454682996,\n  \"value\": 50\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Dimmer",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a dimmer&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "post",
    "url": "/dimmer/set_level",
    "title": "Set level",
    "name": "set_dimmer_level",
    "group": "Dimmer",
    "description": "<p>Set the level of a dimmer node</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Dimmer's ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "value",
            "description": "<p>new level value in [0, 99]</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request example",
          "content": "{\n    'node_id' : '4',\n    'value' : '50'\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Reasons: &quot;Wrong input parameter(s) were provided&quot;, &quot;Argument 'location' has incorrect type (expected int, got str).</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a dimmer&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Dimmer",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[<old-value>, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/network/dimmers",
    "title": "Dimmers",
    "name": "get_dimmers_list",
    "group": "Network",
    "description": "<p>Get a lists all dimmers nodes in the network</p>",
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"2\": \"Unknown: type=4c42, id=3134\",\n  \"3\": \"...\"\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array keyed by nodes' IDs with values as nodes' &quot;product names&quot;</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network"
  },
  {
    "type": "get",
    "url": "/network/info",
    "title": "Overview",
    "name": "get_network_info",
    "group": "Network",
    "description": "<p>Gets an overview of Z-Wave network in a JSON format</p>",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array indexed by node IDs. See example below.</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "{\n    \"1\": {\n        \"Is Ready\": true,\n        \"Neighbours\": [\n            2,\n            3\n        ],\n        \"Node ID\": \"1\",\n        \"Node location\": \"\",\n        \"Node name\": \"\",\n        \"Node type\": \"Static PC Controller\",\n        \"Product name\": \"ZME_UZB1 USB Stick\",\n        \"Query Stage\": \"Complete\",\n        \"Query Stage (%)\": 100       # readiness level: onnce at 100%, the\n                                     # node is ready to be used.\n    },\n    \"2\": {\n        \"Is Ready\": true,\n        \"Neighbours\": [\n            1,\n            3\n        ],\n        \"Node ID\": \"2\",\n        \"Node location\": \"\",\n        \"Node name\": \"\",\n        \"Node type\": \"Home Security Sensor\",\n        \"Product name\": \"MultiSensor 6\",\n        \"Query Stage\": \"Complete\",\n        \"Query Stage (%)\": 100\n    },\n    \"3\": {\n        \"Is Ready\": true,\n        \"Neighbours\": [\n            1,\n            2\n        ],\n        \"Node ID\": \"3\",\n        \"Node location\": \"\",\n        \"Node name\": \"\",\n        \"Node type\": \"Light Dimmer Switch\",\n        \"Product name\": \"Unknown: type=4c42, id=3134\",\n        \"Query Stage\": \"Complete\",\n        \"Query Stage (%)\": 100\n    },\n    \"Network Home ID\": \"0xd6297cb6\"\n}",
          "type": "OBJECT"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network"
  },
  {
    "type": "get",
    "url": "/network/nodes_configuration",
    "title": "Configuration",
    "name": "get_nodes_configuration",
    "group": "Network",
    "description": "<p>Gets the list of configuration parameters for all nodes in a JSON format.</p>",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON  Associative array keyed by node's IDs, with an item for any known node in the network. For a given node type, each parameter is univocally identified by its &quot;index&quot;.</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "{\n    \"Network Home ID\": \"0xe221b13f\",\n    \"2\": {\n        \"72057594081706020\": {\n            \"command_class\": 112,\n            \"data\": \"No\",\n            \"data_items\": [\n                \"No\",\n                \"Yes\"\n            ],\n            \"genre\": \"Config\",\n            \"index\": 2,\n            \"is_read_only\": false,\n            \"is_write_only\": false,\n            \"label\": \"Wake up 10 minutes on Power On\",\n            \"node_id\": 2,\n            \"type\": \"List\",\n            \"units\": \"\",\n            \"value_id\": 72057594081706020\n        },\n    },\n    ...\n}",
          "type": "Object"
        }
      ]
    },
    "examples": [
      {
        "title": "The following table gives some examples of parameters for an Aeotec MultiSensor 6:",
        "content": "index  label                    note\n-----------------------------------------------------------------------\n    4  \"Enable Motion Sensor\"   Motion sensor's sensitivity level\n  101  \"Group 1 Reports\"        Which report are to be sent in Report\n                                Group 1 -- set 241 to send all.\n  111  \"Group 1 Interval\"       Seconds between two consecutive Group1\n                                measurements",
        "type": "json"
      }
    ],
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network"
  },
  {
    "type": "get",
    "url": "/network/nodes",
    "title": "Nodes",
    "name": "get_nodes_list",
    "group": "Network",
    "description": "<p>Get a list of all the nodes in the network.</p>",
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"1\": \"Z-Stick Gen5\",\n  \"2\": \"MultiSensor 6\",\n  \"3\": \"[not ready]\"\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array keyed by nodes' IDs with values as nodes' &quot;product names&quot;</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network"
  },
  {
    "type": "get",
    "url": "/network/sensors",
    "title": "Sensors",
    "name": "get_sensors_list",
    "group": "Network",
    "description": "<p>Get a lists of all sensors nodes in the network.</p>",
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"2\": \"MultiSensor 6\",\n  \"3\": \"[not ready]\"\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array keyed by nodes' IDs with values as nodes' &quot;product names&quot;</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network"
  },
  {
    "type": "post",
    "url": "/network/hard_reset",
    "title": "Hard Reset",
    "name": "network_hard_reset",
    "group": "Network",
    "description": "<p>Hard-resets the network's controller. You shouldn't call this method before excluding (removing) all connected nodes, but you can force to do so at your own risk.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Bool",
            "optional": false,
            "field": "force",
            "defaultValue": "False",
            "description": "<p>Must be set to True to force reset of a network with included nodes.</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "NetworkHasNodes",
            "description": "<p>A reset was attempted on a network with nodes while <code>force=False</code>.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[True, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/network/reset",
    "title": "Reset",
    "name": "network_reset",
    "group": "Network",
    "description": "<p>Soft-resets the network's controller. Warning! This will power-cycle the controller: the associated device file might change. The network will also be restarted.</p>",
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[True, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/network/start",
    "title": "Start",
    "name": "network_start",
    "group": "Network",
    "description": "<p>Starts the OZW controller and software representation of the network</p>",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error response",
          "content": "[False, 'System already started. Skipping...']",
          "type": "Object"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[True, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/network/stop",
    "title": "Stop",
    "name": "network_stop",
    "group": "Network",
    "description": "<p>Stops the OZW software representation of the network. Warning! This is broken on some platforms, see Bug <a href=\"https://github.com/OpenZWave/python-openzwave/issues/202\">https://github.com/OpenZWave/python-openzwave/issues/202</a></p>",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Error response (reason unknown)",
          "content": "[False, '[reason]']",
          "type": "Object"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Network",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[True, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/node/add",
    "title": "Add",
    "name": "add_node",
    "group": "Node",
    "description": "<p>Adds a (non-controller) node to the network by switching the controller into &quot;inclusion&quot; mode for a configurable number of seconds. Physical action is required on the node device to be added.</p>",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>The newly added node's full configuration structure.</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  {\n    \"capabilities\": {\n        \"beaming\": 0,\n        \"listening\": 0,\n        \"routing\": 0,\n        \"zwave_plus\": 0\n    },\n    \"groups\": {\n        \"1\": {\n            \"label\": \"Group 1\"\n        }\n    },\n    \"location\": \"\",\n    \"name\": \"\",\n    \"neighbors\": {},\n    \"node_id\": 3,\n    \"product_name\": \"Unknown: type=4c42, id=3134\",\n    \"product_type\": \"0x4c42\",\n    \"values\": {\n        \"72057594093076481\": {\n            \"data\": 0,\n            \"genre\": \"User\",\n            \"label\": \"Level\",\n            \"node_id\": 3,\n            \"units\": \"\",\n            \"value_id\": 72057594093076481\n        },\n    ...\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "InclusionError",
            "description": "<p>The reason is specified in the message: &quot;Network not started&quot;, &quot;Timeout. Inclusion cancelled&quot;, &quot;Unknown error&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node"
  },
  {
    "type": "get",
    "url": "/node/<node_id>/location",
    "title": "Location",
    "name": "get_location",
    "group": "Node",
    "description": "<p>Retreve the location string of a given node</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Node's ID</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[<old-value>, 'OK']",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>Reason: &quot;No such node&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/node/<node_id>/name",
    "title": "Name",
    "name": "get_name",
    "group": "Node",
    "description": "<p>Gets name of a given node</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Node' ID</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[<old-value>, 'OK']",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>Reason: &quot;No such node&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/node/<node_id>/neighbours",
    "title": "Neighbours",
    "name": "get_neighbours",
    "group": "Node",
    "description": "<p>Gets a list of a node's neighbours</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Node's ID</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array(Number, ...)</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[2, 3]",
          "type": "Object"
        }
      ]
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>Reason: &quot;No such node&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/node/<node_id>/parameter/<index>",
    "title": "Parameter",
    "name": "get_parameter",
    "group": "Node",
    "description": "<p>Gets the value of a node's configuration parameter</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Node's ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "index",
            "description": "<p>Parameter's index</p>"
          }
        ]
      }
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Number/String",
            "optional": false,
            "field": "...",
            "description": "<p>The parameter's value</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;.</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Index overflow: &quot;Value too large to convert to uint8_t&quot; .</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node"
  },
  {
    "type": "get",
    "url": "/node/remove",
    "title": "Remove",
    "name": "remove_node",
    "group": "Node",
    "description": "<p>Removes a (non-controller) node to the network by switching the controller into &quot;exclusion&quot; mode for a configurable number of seconds. Physical action is required on the node device to be added.</p>",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "obj",
            "optional": false,
            "field": "...",
            "description": "<p>The removed node</p>"
          }
        ]
      }
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "InclusionError",
            "description": "<p>The reason is specified in the message: &quot;Network not started&quot;, &quot;Timeout. Exclusion cancelled&quot;, &quot;Unknown error&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node"
  },
  {
    "type": "post",
    "url": "/node/set_location",
    "title": "Set location",
    "name": "set_location",
    "group": "Node",
    "description": "<p>Set a node's &quot;location&quot; string</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Nodes's ID</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "value",
            "description": "<p>The new location value</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request example",
          "content": "{\n    \"node_id\" : 4,\n    \"value\" : \"kitchen\"\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Reasons: &quot;Wrong input parameter(s) were provided&quot;, &quot;Argument 'location' has incorrect type (expected str, got int).</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>Reason: &quot;No such node&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[<old-value>, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "post",
    "url": "/node/set_name",
    "title": "Set name",
    "name": "set_name",
    "group": "Node",
    "description": "<p>Sets the name string of a given node</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Nodes's ID</p>"
          },
          {
            "group": "Parameter",
            "type": "String",
            "optional": false,
            "field": "value",
            "description": "<p>new name value</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request-Example :",
          "content": "{\n    'node_id' : '4',\n    'value' : 'A401-multisensor'\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Reasons: &quot;Wrong input parameter(s) were provided&quot;, &quot;Argument 'location' has incorrect type (expected str, got int).</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>Reason: &quot;No such node&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[<old-value>, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "post",
    "url": "/node/set_parameter",
    "title": "Set parameter",
    "name": "set_parameter",
    "group": "Node",
    "description": "<p>Sets the value of a given node's configuration parameter</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Nodes's ID</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "index",
            "description": "<p>Parameter's index</p>"
          },
          {
            "group": "Parameter",
            "type": "Number/String",
            "optional": false,
            "field": "value",
            "description": "<p>Parameter's value</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "size",
            "description": "<p>Parameter's size</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request-Example :",
          "content": "{\n    'node_id' : '4',\n    'index' : '101',\n    'value' : '227',\n    'size' : '4'\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Reasons: &quot;Wrong input parameter(s) were provided&quot;, &quot;Value too large to convert to uint8_t&quot; (overflow in any of <code>index</code>, <code>size</code>, <code>value</code>).</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;Command failed&quot;, &quot;No such node&quot;, &quot;Not ready&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Node",
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON array</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "[True, 'OK']",
          "type": "Object"
        }
      ]
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/battery",
    "title": "Battery",
    "name": "battery",
    "group": "Sensor",
    "description": "<p>Gets the battery level of a sensor, in a JSON format.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"battery\",\n  \"updateTime\": 1454684168,\n  \"value\": 100\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/humidity",
    "title": "Humidity",
    "name": "humidity",
    "group": "Sensor",
    "description": "<p>Gets the humidity reading of a sensor in a JSON format</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"humidity\",\n  \"updateTime\": 1454682996,\n  \"value\": 21\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/luminance",
    "title": "Luminance",
    "name": "luminance",
    "group": "Sensor",
    "description": "<p>Gets the luminance reading of a sensor in a JSON format</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's unique ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"luminance\",\n  \"updateTime\": 1454682996,\n  \"value\": 49\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/motion",
    "title": "Motion (burglar)",
    "name": "motion",
    "group": "Sensor",
    "description": "<p>Gets the motion (burglar) reading of a sensor in a JSON format.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's unique ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"sensor\",\n  \"updateTime\": 1454682996,\n  \"value\": true\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/readings",
    "title": "Readings",
    "name": "readings",
    "group": "Sensor",
    "description": "<p>Gets all measureament readings of a sensor, in a JSON format</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"battery\": 100,\n  \"controller\": \"Pi lab1\",\n  \"humidity\": 22,\n  \"location\": \"Room A401\",\n  \"luminance\": 60,\n  \"motion\": false,\n  \"sensor\": 2,\n  \"temperature\": 30.0,\n  \"updateTime\": 1454682568\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "post",
    "url": "/sensor/set_parameter_all",
    "title": "Set parameter for all",
    "name": "set_parameter_all",
    "group": "Sensor",
    "description": "<p>Set a configuration parameter for all sensor nodes in the network.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "index",
            "description": "<p>Parameter's index</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "value",
            "description": "<p>Parameter's new value</p>"
          },
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "size",
            "description": "<p>Parameter's size</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Request Example",
          "content": "{\n    'index' : '101',\n    'value' : '227',\n    'size' : '4'\n}",
          "type": "Object"
        }
      ]
    },
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array keyed by nodes' IDs</p>"
          }
        ]
      },
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"2\": [true, \"OK\"],\n  \"3\": [false, \"Not ready\"],\n  \"4\": [false, \"Command failed\"],\n  ...\n}",
          "type": "Object"
        }
      ]
    },
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "WrongInput",
            "description": "<p>Reasons: &quot;Wrong input parameter(s) were provided&quot;.</p>"
          },
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;Network not started&quot;.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor"
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/temperature",
    "title": "Temperature",
    "name": "temperature",
    "group": "Sensor",
    "description": "<p>Gets the temperature reading of a sensor in a JSON format.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's ID</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"temperature\",\n  \"updateTime\": 1454682568,\n  \"value\": 30.4\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "type": "get",
    "url": "/sensor/<node_id>/ultraviolet",
    "title": "Ultraviolet",
    "name": "ultraviolet",
    "group": "Sensor",
    "description": "<p>Gets the ultraviolet reading of a sensor in a JSON format.</p>",
    "parameter": {
      "fields": {
        "Parameter": [
          {
            "group": "Parameter",
            "type": "Number",
            "optional": false,
            "field": "node_id",
            "description": "<p>Sensor's unique ID.</p>"
          }
        ]
      }
    },
    "success": {
      "examples": [
        {
          "title": "Success response",
          "content": "{\n  \"controller\": \"Pi lab1\",\n  \"location\": \"Room A401\",\n  \"sensor\": 2,\n  \"type\": \"ultraviolet\",\n  \"updateTime\": 1454682996,\n  \"value\": 0.2\n}",
          "type": "Object"
        }
      ],
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "type": "Object",
            "optional": false,
            "field": "...",
            "description": "<p>JSON associative array. See example below.</p>"
          }
        ]
      }
    },
    "version": "0.0.0",
    "filename": "./flask-main.py",
    "groupTitle": "Sensor",
    "error": {
      "fields": {
        "Error 4xx": [
          {
            "group": "Error 4xx",
            "optional": false,
            "field": "QueryFail",
            "description": "<p>The query failed. Possible reasons: &quot;No such node&quot;, &quot;Not ready&quot;, &quot;Not a sensor&quot;.</p>"
          }
        ]
      }
    }
  },
  {
    "success": {
      "fields": {
        "Success 200": [
          {
            "group": "Success 200",
            "optional": false,
            "field": "varname1",
            "description": "<p>No type.</p>"
          },
          {
            "group": "Success 200",
            "type": "String",
            "optional": false,
            "field": "varname2",
            "description": "<p>With type.</p>"
          }
        ]
      }
    },
    "type": "",
    "url": "",
    "version": "0.0.0",
    "filename": "./doc/main.js",
    "group": "_home_marcoep_projects_hepia_teaching_master_iot_Smart_Building_doc_main_js",
    "groupTitle": "_home_marcoep_projects_hepia_teaching_master_iot_Smart_Building_doc_main_js",
    "name": ""
  }
] });
