#!/usr/bin/python3

import sys
import time
import logging
import functools
import configparser
import tuyacloud

range = 2
cool_fan_speed = '3'
standby_fan_speed = '1'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M')

class Thermostat:
    def __init__(self, ac, setpoint, range):
        self.ac = ac
        self.setpoint = setpoint
        self.range = range
        self.state = self.enter_state_off

    def run(self):
        while True:
            self.state = self.state()
            time.sleep(60*3)

    def enter_state_off(self):
        logging.info("turning off")
        self.ac.set_power(False)
        self.ac.commit()
        return functools.partial(self.run_state_off, 0)

    def run_state_off(self, iteration):
        self.ac.refresh()
        temp = self.ac.get_current_temperature()
        logging.info("current temperature: %d", temp)
        if temp >= self.setpoint + self.range:
            return self.enter_state_cooling()
        else:
            if iteration % 5 == 3:
                logging.info("spinning up fan to check temperature")
                self.ac.set_mode('wind')
                self.ac.set_fan_speed(standby_fan_speed)
                self.ac.set_power(True)
                self.ac.commit()
            elif iteration % 5 == 4:
                logging.info("stopping fan after checking temperature")
                self.ac.set_power(False)
                self.ac.commit()
            return functools.partial(self.run_state_off, iteration+1)

    def enter_state_cooling(self):
        logging.info("turning on")
        self.ac.set_mode('cold')
        self.ac.set_setpoint_temperature(self.setpoint - self.range)
        self.ac.set_fan_speed(cool_fan_speed)
        self.ac.set_power(True)
        self.ac.commit()

        return self.run_state_cooling

    def run_state_cooling(self):
        self.ac.refresh()
        temp = self.ac.get_current_temperature()
        logging.info("current temperature: %d", temp)
        if temp < self.setpoint:
            return self.enter_state_shut_down()
        else:
            return self.run_state_cooling

    def enter_state_shut_down(self):
        logging.info("switching to fan-only")
        self.ac.set_mode('wind')
        self.ac.set_fan_speed(standby_fan_speed)
        self.ac.commit()
        return self.enter_state_off

def main(argv):
    config_file = argv[0]
    ac_name = argv[1]
    setpoint = int(argv[2])

    config = configparser.ConfigParser()
    config.read(config_file)
    print("running %s at temperature %d" % (ac_name, setpoint))
    api = tuyacloud.TuyaAPI(config['TuyaCredentials']['User'], config['TuyaCredentials']['Password'],
        config['TuyaAccess']['Id'], config['TuyaAccess']['Key'])

    devices = api.get_devices()
    device = next((dev for dev in devices if dev['name'] == ac_name), None)

    if device is None:
        print("device %s not found" % ac_name)
        return 1

    ac = tuyacloud.AirConditioner(api, device)
    thermostat = Thermostat(ac, setpoint, range)
    thermostat.run()

if __name__ == "__main__":
    main(sys.argv[1:])
