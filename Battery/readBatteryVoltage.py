import machine
from machine import ADC

numADCreadings = const(100)
def readBatteryLevel():
    adc = machine.ADC(0)
    adcread = adc.channel(attn=ADC.ATTN_2_5DB, pin='P16')
    samplesADC = [0.0]*numADCreadings; meanADC = 0.0
    i = 0
    while (i < numADCreadings):
        adcint = adcread()
        samplesADC[i] = adcint
        meanADC += adcint
        i += 1
    meanADC /= numADCreadings
    varianceADC = 0.0
    for adcint in samplesADC:
        varianceADC += (adcint - meanADC)**2
    varianceADC /= (numADCreadings - 1)

    return (meanADC*1400/4095)
