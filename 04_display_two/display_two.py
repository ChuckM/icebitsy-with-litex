#!/usr/bin/env python3
#
# Written by Chuck McManis September, 2021
# still just easy stuff
#
from migen import *
from litex.build.generic_platform import *
from litex_boards.platforms.icebreaker_bitsy import Platform
from led7segment import SevenSegmentLedDisplay

# we'll call it a bitsy of type Platform()
bitsy = Platform()


class Counter(Module):
	def __init__(self, count_speed):
		#
		# This is going to be our count (now 16 bits wide)
		#
		count = Signal(16)
		gled = bitsy.request("user_ledg_n")

		#
		# The 'standard' divide by n clock divider
		#
		divisor = Signal(24)
		ticks = int((500e6/(count_speed * bitsy.default_clk_period))) - 1

		self.sync += [
			divisor.eq(divisor + 1),
			If(divisor == ticks,
				divisor.eq(0),
				#
				# We have to add several new tests for roll over in the 
				# hundreds and thousands places, as well as a new reset
				# test for 9999.
				#
				If(count == 0x9999,
					gled.eq(~gled),
					count.eq(0)
				).Elif(count[:12] == 0x999,
					count.eq(count + 0x667)
				).Elif(count[:8] == 0x99,
					count.eq(count + 0x67)
				).Elif(count[:4] == 9,
					count.eq(count + 0x7)
				).Else(
					count.eq(count + 1)
				)
			),
		]
		self.comb += [ ]
		# we will put the 'upper' two digits on PMOD1
		self.submodules += [SevenSegmentLedDisplay(bitsy, "PMOD1", 
															value=count[8:])]
		# and the 'lower' two digits on PMOD2
		self.submodules += [SevenSegmentLedDisplay(bitsy, "PMOD2", 
															value=count[:8])]


#
# Now instantiate a counter, which instantiates an LED display
# sub-module which is showing the count.
#
count_module = Counter(10);

#
# And "build" this into a bit file
#

bitsy.build(count_module)

