from machine import ADC
import sendData
from machine import Timer
import time
import utime
from machine import RTC
import readBatteryVoltage

# TMP-36 sensor
# From -40°C (0,1V) to 125°C (1,7V)

ADC_PIN_TMP36 = 'G5' #G5									# ADC Pin number on which the TMP-36 is connected
T_MAX_MV = 1100 								# the max input of the ADC in mV
V_TO_MV = 1000									# To convert V to mV
ADC_MAX_VAL = 4095								# Max digital value returned by ADC
PRECISION_SCALE = 1 							# The precision we want
OFFSET_MV = 500 * PRECISION_SCALE 						# The offset of the sensor
SCALE_FACTOR = 10 * PRECISION_SCALE				# The scaling factor as workaround of no float in micropython

def getTemperature():
	global ADC_PIN_TMP36
	global T_MAX_MV
	global V_TO_MV
	global ADC_MAX_VAL
	global PRECISION_SCALE
	global OFFSET_MV
	global SCALE_FACTOR

	adc_tmp36 = ADC(0)
	apin_tmp36 = adc_tmp36.channel(pin=ADC_PIN_TMP36)
	rawTemp = 0
	for x in range(0, 100):
		adc_value = apin_tmp36.value()
		# read value (0~1024) then converted in mV then scaled to get more precision
		tMV = adc_value * (T_MAX_MV /  ADC_MAX_VAL)* PRECISION_SCALE
		# convert th mV received to temperature
		rawTemp += (tMV - OFFSET_MV) / 10

	return (rawTemp/100)

rtc = RTC()
rtc.ntp_sync('fr.pool.ntp.org')
sendData.connectLocalBox()

while 1==1:
	data = '{"temperature": %s, "timestamp": "%s", "battery" : %s}' % (getTemperature(),rtc.now(), readBatteryVoltage.readBatteryLevel())
	sendData.sendData(host='http://192.168.1.15', port=1338, data=data)
	time.sleep(300)
