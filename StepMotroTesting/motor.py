# import required libs
import time
from machine import Timer, Pin

LOW=0
HIGH=1
# be sure you are setting pins accordingly
# GPIO10,GPIO9,GPIO11,GPI25

in1=Pin('GP1', mode=Pin.OUT)
in2=Pin('GP5', mode=Pin.OUT)
in3=Pin('GP3', mode=Pin.OUT)
in4=Pin('GP4', mode=Pin.OUT)

StepPins = [in1,in2,in3,in4]
StepPinsPos = [1,2,3,4]
# Set all pins as output
for pin in StepPins:
  pin.value(LOW)
 
#wait some time to start
time.sleep_us(500000)
 
# Define some settings
StepCounter = 0
WaitTime_us = 1500
 
# Define simple sequence
StepCount1 = 4
Seq1 = [[1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1]]

 
# Define advanced sequence
# as shown in manufacturers datasheet
StepCount2 = 8
Seq2 = [[1,0,0,0], [1,1,0,0], [0,1,0,0], [0,1,1,0], [0,0,1,0], [0,0,1,1], [0,0,0,1], [1,0,0,1]]

 
#Full torque clockwise
StepCount3 = 4
Seq3 = []
Seq3 = [3,2,1,0]
Seq3[0] = [0,0,1,1]
Seq3[1] = [1,0,0,1]
Seq3[2] = [1,1,0,0]
Seq3[3] = [0,1,1,0]
 
#Full torque anticlockwise
StepCount4 = 4
Seq4 = []
Seq4 = [3,2,1,0]
Seq4[3] = [0,0,1,1]
Seq4[2] = [1,0,0,1]
Seq4[1] = [1,1,0,0]
Seq4[0] = [0,1,1,0]
# set

 
# Start main loop

while 1==1:
  for i in range(0, 2048):
    Seq = Seq3
    StepCount = StepCount3
    for pin in range(0, 4):
      xpin = StepPins[pin]
      if Seq[StepCounter][pin]!=0:
        xpin.value(HIGH)
      else:
        xpin.value(LOW)
    StepCounter += 1

  # If we reach the end of the sequence
  # start again
    if (StepCounter==StepCount):
      StepCounter = 0
    if (StepCounter<0):
      StepCounter = StepCount

  # Wait before moving on
    time.sleep_us(WaitTime_us)
  