#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""OVH DynHost IP Updater.

Updates at least every 15 minutes the DynHost Record IP of the server.
Uses the OVH API.

Requires:
* ovh - https://github.com/ovh/python-ovh
* ipgetter - https://github.com/phoemur/ipgetter
"""
import re
import time
import os.path
import ConfigParser
import logging

import ovh
import ipgetter

# Creation of the logger
logger = logging.getLogger('OVH DynHost Updater')
logger.setLevel(logging.INFO)
# create console handler and set level to info
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)

# The paths in the OVH API (api.ovh.com)
UPDATE_PATH = "/domain/zone/{zonename}/dynHost/record/{id}"
REFRESH_PATH = "/domain/zone/{zonename}/refresh"

# The file where the IP will be stored
# As the script doesn't run continuosly, we need to retreive the IP somewhere...
IP_FILE = "stored_ip.txt"

# The period between two forced updates of the IP on the OVH server.
# If you launch the script every minute, this reduces the number of calls to the
# OVH server.
MIN_UPDATE_TIME = 15  # In minutes [1-59]

# Regex for checking IP strings
check_re = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')

def get_conf():
    """Get the configuration from the file `subdomain.conf`.

    Mandatory sections/values:
    - zone/name
    - subdomain/id
    - subdomain/name
    """
    config = ConfigParser.SafeConfigParser()
    config.read('subdomain.conf')

    try:
        zonename = config.get('zone', 'name')
        dynhost_id = config.get('subdomain', 'id')

        subdomain = config.get('subdomain', 'name')
    except ConfigParser.Error, error:
        logger.error("Configuration File Error: %s", error)
        return None, None

    path = {
        'update': UPDATE_PATH.format(zonename=zonename, id=dynhost_id),
        'refresh': REFRESH_PATH.format(zonename=zonename)
        }

    return path, subdomain

def get_stored_ip():
    """Return the IP stored in the file `IP_FILE` or False if not conform."""
    try:
        with open(IP_FILE, "r") as fd:
            ip = fd.read()
            fd.close()

        result = check_re.match(ip)
        if result:
            return result.group(0)
        # No match. Not blocking.
        logger.warning("Bad stored IP. No regex match.")
        return False

    except IOError:
        # No file found.
        logger.warning("No such file: %s", IP_FILE)
        return None

def store_ip(ip):
    """Write the IP into the file `IP_FILE`."""
    try:
        with open(IP_FILE, 'w') as fd:
            fd.write(ip)
            fd.close()
        return True
    except IOError:
        # Not possible to write a file.
        logger.error("Impossible to write %s", os.path.abspath(IP_FILE))
        return False

def get_dynhost_ip():
    """Get the DynHost IP record from OVH server using the API."""
    client = ovh.Client()

    dynhost_current = client.get(UPDATE_PATH)

    if 'ip' in dynhost_current:
        return dynhost_current['ip']
    else:
        logger.warning("No IP returned by OVH...")
        return False

def set_dynhost_ip(ip):
    """Set the IP using the OVH API."""
    # Get the conf
    paths, subdomain = get_conf()

    if not path or not subdomain:
        logger.error("No path or subdomain!")
        return False

    params = {"ip": ip, "subDomain": subdomain}

    client = ovh.Client()

    try:
        client.put(path['update'], **params)
        client.post(path['refresh'])
    except ovh.exceptions.NotGrantedCall, error:
        logger.error("OVH Not Granted Call: %s", error)
        return False
    return True


def compare():
    """Compare the current IP and the stored IP.
    Update the DynHost IP if different.
    """
    stored_ip = get_stored_ip()
    logger.info("Stored IP: %s", stored_ip)
    current_ip = ipgetter.myip()
    logger.info("Current IP: %s", current_ip)

    # Check if there is no difference between stored IP and current IP
    if not stored_ip or (stored_ip != current_ip):
        logger.info("DynHost IP updated! [New IP]")
        dynhost_ip = set_dynhost_ip(current_ip)
        if dynhost_ip:
            store_ip(current_ip)
        else:
            # This will force update next call
            store_ip('Error')

    # Set each 15 minutes the Dynhost IP
    if (time.gmtime().tm_min % MIN_UPDATE_TIME) == 0:
        logger.info("DynHost IP updated! [15 min]")
        set_dynhost_ip(current_ip)

if __name__ == "__main__":
    compare()
