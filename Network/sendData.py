import machine
from network import WLAN
import urequests
import ujson

def connectLocalBox(configFilePath):
    f = open(configFilePath, 'r')
    config=ujson.load(f)
    f.close()

    wlan = WLAN(mode=WLAN.STA)
    wlan.ifconfig(config=(config["ip"], config["mask"],config["gateway"], config["dns"]))
    wlan.scan()
    wlan.connect(config["ssid"], auth=(WLAN.WPA2, config["password"]))
    while not wlan.isconnected():
        pass
    return wlan;


def send(host, port, path='', data='', headers={}):
    url = '%s:%s/%s' % (host, port, path)
    resp = urequests.request('POST', url, json=data, headers=headers)
    return resp


def get(url):
    resp = urequests.request('GET', url)
    return resp
