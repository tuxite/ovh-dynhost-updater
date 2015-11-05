#!/usr/bin/python
# -*- encoding: utf-8 -*-
"""OVH Consumer Key Request

Script adapted from https://github.com/ovh/python-ovh/README.rst
"""
import ovh

from updater import get_conf

if __name__ == "__main__":
    # Create a client using configuration
    client = ovh.Client()

    # Get the subdomain configuration
    path, subdomain = get_conf()
    if not path:
        exit("No path found")

    # Request RO, /me API access
    access_rules = [
        #{'method': 'GET', 'path': "/me"},
        {'method': 'GET', 'path': path},
        {'method': 'PUT', 'path': path},
    ]

    # Request token
    validation = client.request_consumerkey(access_rules)

    print "Please visit %s to authenticate" % validation['validationUrl']
    raw_input("and press Enter to continue...")

    # Print nice welcome message
    print "The 'consumerKey' is '%s'" % validation['consumerKey']
