#!/usr/bin/python3

import sys
import logging
import configparser
import tuyacloud

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M')

def main(argv):
    config_file = argv[0]

    config = configparser.ConfigParser()
    config.read(config_file)

    api = tuyacloud.TuyaAPI(config['TuyaCredentials']['User'], config['TuyaCredentials']['Password'],
        config['TuyaAccess']['Id'], config['TuyaAccess']['Key'])

    devices = api.get_devices()

    for dev in devices:
        print("device %s has local key %s" % (dev['name'], dev['localKey']))
    print("done")

if __name__ == "__main__":
    main(sys.argv[1:])
