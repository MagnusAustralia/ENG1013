# TeamC24-M2-SS2.py
# Created By: William
# Created Date: 19 August 2026
# Version: 1.0
from pymata4 import pymata4
import time

# Globals
isR1Running = False

# Input pins
pb1 = 3
pb2 = 4
ds2 = 5

# Output pins -
#   tl = Traffic Light, where the specific LED colour is then mentioned
#   pl = Pedestrian Light, where the specified colour is then mentioned
tl4R = 8
tl4G = 9
tl4B = 10
tl5R = 11
tl5G = 12
tl5B = 13

pl1R = 14
pl1G = 15
pl2R = 16
pl3G = 17

board = pymata4.Pymata4()

board.set_pin_mode_digital_input(pb1)
board.set_pin_mode_digital_input(pb2)

board.set_pin_mode_digital_output(tl5R)


# Functions
def main():
	try:
		while True:
			if board.digital_read(pb1)[0] or board.digital_read(pb2)[0]:
				time.sleep(2)
				if board.digital_read(tl5R)[0] == 0:
					# Set TL5 to Yellow
					time.sleep(3)
				else:
					pass
					# Set TL4 to Yellow
				# Turn PL1/PL2 green for 3 seconds, then flash red for 2s before resetting to solid red
				# Turn TL4 to green
	except KeyboardInterrupt:
		print("Program stopped")
	finally:
		board.shutdown()


# Main
if __name__ == "__main__":
	main()
