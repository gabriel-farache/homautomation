from network import Bluetooth
from machine import RTC
import time
import ubinascii
import sendData
import pycom

def extractTemperature(data):
    temp = (data[2] & ~(1 << 7)) + (data[3] / 100)
    sign = (data[2] >> 7) & 1
    if sign == 0:
        return round(temp, 2)
    return round(-1 * temp, 2)


def extractHumidity(data):
    return data[1] * 0.5


def extractPressure(data):
    pres = (data[4] << 8) + data[5] + 50000
    return pres / 100

sendData.connectLocalBox('/flash/config.json')
rtc = RTC()
rtc.ntp_sync('fr.pool.ntp.org')

bt = Bluetooth()
try:
    bt.start_scan(-1)
except:
    bt.stop_scan()
    bt.start_scan(-1)

while True:
    try:
        adv = bt.get_adv()
        if adv:
            data = str(adv.data, "utf-8")
            data = str(data.split("#")[1][:8], "utf-8")
            data = ubinascii.a2b_base64(data)
            temperature = extractTemperature(data)
            humidity = extractHumidity(data)
            pressure = extractPressure(data)
            id = str(ubinascii.hexlify(adv.mac), "utf-8")

            content = '{"temperature": %s, "humidity": %s, "pressure" : %s, "mac": %s, "timestamp": "%s"}' % (
                temperature, humidity, pressure, id, rtc.now())
            print(content)
            sendData.send(host='http://192.168.1.15', port=1338, data=content)
            pycom.rgbled(0x007f00)  # green
            time.sleep(0.1)
            pycom.rgbled(0)
            try:
                bt.stop_scan()
            except:
                print("Error stopping...")
            time.sleep(60)
            try:
                bt.start_scan(-1)
            except:
                bt.stop_scan()
                bt.start_scan(-1)
        else:
            time.sleep(0.050)
    except:
        print("Error while sending...")
        pycom.rgbled(0x7f0000)  # red
        time.sleep(0.7)
        pycom.rgbled(0)
