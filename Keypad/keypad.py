from machine import Pin 
# Flexible membrane 16 keys (4x4) keypad
# To get the pressed key, we need to have the intersect of the col and the row
# When a key is pressed, both row and col shall be LOW
# Row must be PULL-UP resistor to get LOW when pressed
# Column must be LOW to allow Row to go from HIGH to LOW when key pressed

# Pins related to keypad Rows
PIN1 = 'GP22'
PIN2 = 'GP17'
PIN3 = 'GP16'
PIN4 = 'GP15'
# Pins related to keypad Columns
PIN5 = 'GP14'
PIN6 = 'GP13'
PIN7 = 'GP12'
PIN8 = 'GP11'

# The keypad keys
KEYPAD= [
			['1', '2', '3', 'A'],
			['4', '5', '6', 'B'],
			['7', '8', '9', 'C'],
			['*', '0', '#', 'D']	
		]
# Instantiate Rows
row1 = Pin(PIN1, mode=Pin.IN, pull=Pin.PULL_UP)
row2 = Pin(PIN2, mode=Pin.IN, pull=Pin.PULL_UP)
row3 = Pin(PIN3, mode=Pin.IN, pull=Pin.PULL_UP)
row4 = Pin(PIN4, mode=Pin.IN, pull=Pin.PULL_UP)
rows = [row1, row2, row3, row4]
# Instantiate Columns
col5 = Pin(PIN5, mode=Pin.OUT)
col6 = Pin(PIN6, mode=Pin.OUT)
col7 = Pin(PIN7, mode=Pin.OUT)
col8 = Pin(PIN8, mode=Pin.OUT)
columns = [col5, col6, col7, col8]

# Initializing the columns to HIGH
for c in range(4):
	columns[c].value(1)

while 0==0:
	# Read all row values
	for r in range(4):
		# Set the cols values to LOW
		for c in range(4):
			columns[c].value(0)
			# If the key is pressed and the col is LOW, the row value will be set to LOW
			if rows[r].value() == 0:
				# Printing the key pressed
				print("%c\n"%(KEYPAD[r][c]))
				# Waiting until the key is released
				while rows[r].value() == 0:
					pass
			# Reset the col value to HIGH
			columns[c].value(1)
