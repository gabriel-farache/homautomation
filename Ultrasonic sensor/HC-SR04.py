import time
import machine
import micropython
from machine import Pin
# HC-SR04 ultrasonic sensor
# 2 pins: Trigger and Echo
# Trigger triggers the wave to get the distance
# Echo listen to the wave 'comeback'
# To trigger: send during 10us a HIGH signal on the Trigger
# Then, on echo, the signal is HIGH while listening to the wave comeback
# Formulae to calculate: t * 10^-2 * 1,7

micropython.alloc_emergency_exception_buf(100)	# To allow error trace in IRQ handler
	
MIN_TO_SEC = 60			# Number of sec in 1 min
SEC_TO_USEC = 1000		# Number of msec in 1 sec

TRIGGER_TIME = 100 		# Trigger time during which send the HIGH signal
TRIGGER_PIN = 'GP11'	# Pin associated to the trigger 
ECHO_PIN = 'GP12'		# Pin associated to the echo

LOW = 0
HIGH = 1

class DistanceSensor:
	def __init__(self, triggerGPIO, echoGPIO):
		self.triggerPin = Pin(triggerGPIO, mode = Pin.OUT)
		self.echoPin = Pin(echoGPIO, mode = Pin.IN)
		# The var to know if we have 28 or 028 in the decimal part
		self.mm_decimal = ""
		# Distance initated to -1 while nothing
		self.mm = -1
		self.cm = -1

	def isDistanceCalculated(self):
		return self.mm != -1 & self.cm != -1

	def setTriggerPinValue(self, value):
		self.triggerPin.value(value)

	def getDistanceString(self):
		return str(self.cm) + "," + self.mm_decimal + str(self.mm) + "cm"
	def changingEdge(self, pin):
		global callback

		# Get the flag which enabled to IRQ
		flags = callback.flags()
		# If rising, start count the time
		if flags & Pin.IRQ_RISING:
			self.raising_time = time.ticks_us()
		# If falling edge, then stop counting the time and calculate the distance
		elif flags & Pin.IRQ_FALLING:
			self.falling_time = time.ticks_us()
			# Get the ellapsed time between RISING and FALLING
			delay = time.ticks_diff(self.raising_time, self.falling_time)
			# We use 17 instead of 0,017
			distance = delay * 17
			# We rescale the distance in cm by separating cm and mm
			self.cm = distance // 1000
			self.mm = distance % 1000
		
			#in case we have a distance like 49028
			# cm = 49
			# mm = 028 but the 0 would be discared so we check it
			if distance % 100 == distance % 1000:
				self.mm_decimal = "0"

		
distanceSensor = DistanceSensor(TRIGGER_PIN, ECHO_PIN)

# Creating the IRQ and saving the callback to get the flag triggering the interruption
callback = distanceSensor.echoPin.irq(trigger = Pin.IRQ_RISING | Pin.IRQ_FALLING, handler = distanceSensor.changingEdge)
# Disabling the trigger
distanceSensor.setTriggerPinValue(LOW)
time.sleep(1)

# Triggering the wave
distanceSensor.setTriggerPinValue(HIGH)
time.sleep_us(TRIGGER_TIME)
distanceSensor.setTriggerPinValue(LOW)

# Waiting until we have the distance
while distanceSensor.isDistanceCalculated() == False:
	time.sleep_us(50000)
	pass

print(distanceSensor.getDistanceString())
