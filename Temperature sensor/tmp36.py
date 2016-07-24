from machine import ADC
# TMP-36 sensor
# From -40°C (0,1V) to 125°C (1,7V)

ADC_PIN = 'GP3'									# ADC Pin number on which the TMP-36 is connected
T_MAX_MV = 1400 								# the max input of the ADC in mV
V_TO_MV = 1000									# To convert V to mV
ADC_MAX_VAL = 4095								# Max digital value returned by ADC
PRECISION_SCALE = 100 							# The precision we want
OFFSET_MV = 500 * V_TO_MV * PRECISION_SCALE		# The offset of the sensor 
SCALE_FACTOR = 10 * PRECISION_SCALE * V_TO_MV	# The scaling factor as counter-measure of no float in micropython


adc = ADC()
apin = adc.channel(pin=ADC_PIN)
while True:
	input("Get temperature...")
	# read value (0~4095) then converted in mV then scaled to get more precision
	tMV = apin() * V_TO_MV * PRECISION_SCALE
	# convert th mV received to temperature
	rawTemp = (((tMV // ADC_MAX_VAL) * T_MAX_MV) - OFFSET_MV)
	# The temperature unit, without comma: ie: 18°c
	tempCUnit = (rawTemp// SCALE_FACTOR)
	# The value of the comma of the temperature: ie: 0,18°C
	tempCDeci = (rawTemp % SCALE_FACTOR)//1000
	#round the decimal part to get 0,5°C precision
	if tempCDeci < 35:
		tempCDeci = 0
	elif tempCDeci >= 35 and tempCDeci <= 65:
		tempCDeci = 50
	else:
		tempCDeci = 0
		tempCUnit = tempCUnit + 1

	temperature=(tempCUnit, tempCDeci)

	print ("%d,%d °c" % (temperature[0], temperature[1]))

