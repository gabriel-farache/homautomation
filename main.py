# main.py -- put your code here!
import pycom
import time
import sendData
from machine import RTC

pycom.heartbeat(False)

try:
    sendData.connectLocalBox('/flash/config.json')
    rtc = RTC()
    rtc.ntp_sync('fr.pool.ntp.org')
    pycom.rgbled(0x00FF00)
    time.sleep(0.2)
    pycom.rgbled(0)
    time.sleep(0.2)
    pycom.rgbled(0x00FF00)
    time.sleep(0.2)
    pycom.rgbled(0)

except Exception as e:
    print(e)
    pycom.rgbled(0xFF0000)
    time.sleep(0.2)
    pycom.rgbled(0)
    time.sleep(0.2)
    pycom.rgbled(0xFF0000)
    time.sleep(0.2)
    pycom.rgbled(0)
