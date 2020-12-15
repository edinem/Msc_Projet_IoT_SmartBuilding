################################################################################
"""configpi.py -- configuration file for HEPIA's LSDS Smart Building IoT
Z-Wave Lab

This module provides just a bunch of global variables at their default
values.

Usage:

  file_path = os.path.dirname(__file__)
  sys.path.insert(0, file_path)

  import configpi

  controller_name = configpi.name
  ...

"""
################################################################################

# (string) How our controller is called
name = 'Pi lab1'

# (string) Where our controller is installed
location = 'lausanne'

# (string) Wich device file to use for communication with the controller
#    /dev/ttyACMx: for Sigma Designs Modem (kernel driver: cdc_acm)
#    /dev/ttyUSBx, /dev/ttyAMA0 possibly for others
# Use ID to avoid renaming on reset. See also '/etc/udev/rules.d/10-local.rules'
#   "usb-0658_0200-if00": should be the same for Sigma Designs chips (Z-Stick,
#                         UZB)
device = '/dev/serial/by-id/usb-0658_0200-if00'

# (string) Path to the low-level system's openzwave configuration. Pre-2020
# labos had "/home/pi/IoTLab/python-openzwave/openzwave/config"
config_path = "/etc/openzwave/"

# (string) Where to store runtime backend artifacts (OZW log, XML options and
# cache files, SQLite DB config file)
user_path = "/tmp/OZW"

# (int:seconds) Timeout for the OZW network to be ready. Too low values might
# cause warnings "Network is not ready after ...s. Continuing anyway"
network_ready_timeout = 60

# (int:seconds) Timeout for the inclusion of a node in the OZW network
controller_operation_timeout = 20

# (int|string:logging.LEVEL) The logging verbosity level as a
# :class:`logging.LEVEL` value
log_level = 'WARNING'

# (str) Format used for logging levels > DEBUG
log_format = '%(asctime)s %(levelname)-8s: %(message)s'

# (str) Format used for logging levels <= DEBUG
log_format_dbg = '%(asctime)s %(levelname)-8s: %(message)s [in %(pathname)s:%(lineno)d]'

# (str) Regex for matching dimmer products
re_dimmer = "dimmer"

# (str) Regex for matching sensor products
re_sensor = "sensor"
