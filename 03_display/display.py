#!/usr/bin/env python3
#
# Written by Chuck McManis September, 2021
# still just easy stuff
#
from migen import *
from litex.build.generic_platform import *
from litex_boards.platforms.icebreaker_bitsy import Platform
#
# This cleans up the code significantly. Here we have abstracted the
# seven segment LED display PMOD into its own module. When we instantiate
# it in our design we will wire it to signals in the design and tell
# the module what PMOD port it is connected to.
#
from led7segment import SevenSegmentLedDisplay

# we'll call it a bitsy of type Platform()
bitsy = Platform()


class Counter(Module):
	"""
		This is a binary coded decimal counter module. When it counts up
		at 'count_speed' counts per second it goes from 00 to 99 and rolls
		over.
	"""
	def __init__(self, count_speed):
		#
		# This is going to be our count
		#
		count = Signal(8)
		gled = bitsy.request("user_ledg_n")

		#
		# The 'standard' divide by n clock divider
		#
		divisor = Signal(24)
		ticks = int((500e6/(count_speed * bitsy.default_clk_period))) - 1

		#
		# The sequential logic increments the counter in 'count' at a rate
		# determined by 'count_speed'. (it is in units of counts per second)
		# Something to notice here is that the count is an 8 bit binary value
		# but the logic "jumps" it by 7 when it hits 9. In this way 0x09 -> 0x10
		# and any time the last four bits are 0x9 it jumps. This makes it
		# a binary coded decimal counter and the display shows 00 -> 99 before
		# rolling over again.
		#
		self.sync += [
			divisor.eq(divisor + 1),
			If(divisor == ticks,
				divisor.eq(0),
				gled.eq(~gled),
				If(count == 0x99,
					count.eq(0)
				).Elif(count[:4] == 9,
					count.eq(count + 0x7)
				).Else(
					count.eq(count + 1)
				)
			),
		]
		self.comb += [ ]
		#
		# This bit instantiates the SevenSegmentLedDisplay module and
		# "connects" the count signal to the signal 'value' in the
		# module.
		#
		# Migen takes the datastructure of modules and elaborates them
		# into a single module and then optimizes by eliminating dead
		# branches and redundant code, Etc.
		#
		self.submodules += [SevenSegmentLedDisplay(bitsy, "PMOD1", 
															value=count)]
#
# Now instantiate a counter, which instantiates an LED display
# sub-module which is showing the count.
#
count_module = Counter(5);

#
# And "build" this into a bit file
#

bitsy.build(count_module)

