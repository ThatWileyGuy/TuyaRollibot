#!/usr/bin/python3

import requests
import time
import hashlib
import json
import logging

class TuyaAPI(object):
    def __init__(self, phone, passwd, access_id, access_key):
        self.phone = phone
        self.passwd = passwd
        self.access_id = access_id
        self.access_key = access_key
        self.sid = None

        h2 = hashlib.md5()
        h2.update(self.passwd.encode())
        passwdHash = h2.hexdigest()

        logging.debug("attempting phone login")
        cmd = 'tuya.m.user.mobile.passwd.login'
        data = {
            'countryCode': '1',
            'mobile': self.phone,
            'passwd': passwdHash
        }
        resp = self.requestapi(cmd, data)
        logging.debug("result: %s", resp)
        self.sid = resp['sid']

    def requestapi(self, cmd, dataa):
        data = json.dumps(dataa, separators=(',', ':'))
        datastr = data.encode()
        timee = str(int(time.time()))
        h1 = hashlib.md5()
        h1.update(datastr)
        logging.debug("postdata: %s", datastr)
        datam = h1.hexdigest()
        datamd = datam[8:16] + datam[0:8] + datam[24:32] + datam[16:24]
        if self.sid != None:
            signun = "a=%s||clientId=%s||lang=en||os=Magic||postData=%s||sid=%s||time=%s||v=1.0||%s" % (cmd, self.access_id, datamd, self.sid, timee, self.access_key)
            h2 = hashlib.md5()
            h2.update(signun.encode())
            sign = h2.hexdigest()
            logging.debug("signing %s produced %s", signun, sign)
            url = 'https://a1.tuyaus.com/api.json?a=' + cmd + '&clientId=' + self.access_id + '&lang=en&os=Magic&sid=' + self.sid + '&time=' + timee + '&v=1.0&sign=' + sign
        else:
            signun = "a=%s||clientId=%s||lang=en||os=Magic||postData=%s||time=%s||v=1.0||%s" % (cmd, self.access_id, datamd, timee, self.access_key)
            h2 = hashlib.md5()
            h2.update(signun.encode())
            sign = h2.hexdigest()
            logging.debug("signing %s produced %s", signun, sign)
            url = 'https://a1.tuyaus.com/api.json?a=' + cmd + '&clientId=' + self.access_id + '&lang=en&os=Magic&time=' + timee + '&v=1.0&sign=' + sign
        logging.debug("posting: %s", data)
        respr = requests.post(url, data={'postData':data})
        logging.debug("response: %s", respr.text)
        resp = json.loads(respr.text)
        if resp['success'] == True:
            respd = resp['result']
        else:
            respd = False
        return respd
    def get_devices(self):
        cmd = 'tuya.m.device.list'
        data = {}
        resp = self.requestapi(cmd, data)
        devs = resp['devices']
        return devs
    def get_device_name(self, dev):
        cmd = 'tuya.m.device.get'
        data = {
            'devId': dev
        }
        resp = self.requestapi(cmd, data)
        name = resp['name']
        return name
    def set_device_name(self, dev, name):
        cmd = 'tuya.m.device.name.update'
        data = {
            'devId': dev,
            'name': name
        }
        self.requestapi(cmd, data)
        return


class AirConditioner(object):
    def __init__(self, api, json):
        self.api = api
        self.json = json
        self.new_state = {}
        self.refresh()

    def refresh(self):
        cmd = 'tuya.m.device.dp.get'
        data = {
            'devId': self.json['devId']
        }
        self.state = self.api.requestapi(cmd, data)
        logging.debug("new state: %s", self.state)


    def commit(self, attempt=1):
        logging.info("reducing state: %s", self.new_state)
        self.refresh()
        self.new_state = {k: v for k, v in self.new_state.items() if self.state[k] != v}
        if len(self.new_state) == 0:
            logging.info("no new state to commit")
            return

        logging.info("committing state: %s", self.new_state)
        cmd = 'tuya.m.device.dp.publish'
        data = {
            'devId': self.json['devId'],
            'dps': self.new_state
        }
        self.api.requestapi(cmd, data)
        time.sleep(2)
        self.refresh()
        done = True
        for (key, value) in self.new_state.items():
            if self.state[key] != value:
                logging.info("state %s is %s, wanted %s", key, self.state[key], value)
                done = False
        if not done:
            if attempt == 3:
                logging.info("third attempt - giving up")
            else:
                logging.info("committing again")
                time.sleep(2)
                self.commit(attempt+1)
        self.new_state = {}

    def get_current_temperature(self,):
        return self.state['3']

    def get_setpoint_temperature(self):
        return self.state['2']

    def set_setpoint_temperature(self, temp):
        self.new_state['2'] = temp

    def get_power(self):
        return self.state['1']

    def set_power(self, power):
        self.new_state['1'] = power

    def get_mode(self):
        return self.state['4']

    def set_mode(self, mode):
        self.new_state['4'] = mode

    def get_fan_speed(self):
        return self.state['5']

    def set_fan_speed(self, speed):
        self.new_state['5'] = speed

    def get_fault(self):
        return self.state['20']
