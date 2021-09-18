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
	def __init__(self, blink_freq):
		#
		# This is going to be our count
		#
		count = Signal(8)
		self.submodules += [SevenSegmentLedDisplay(bitsy, "PMOD1", 
															value=count)]

		print(f"Counter at {blink_freq} Hz\n")
		############
		# some debug code
		#
		bitsy.add_extension([("heartbeat", 0, Pins("PMOD3:7"))])
		bitsy.add_extension([("heartbeat", 0, Pins("PMOD3:6"))])
		hb = bitsy.request("heartbeat")
		hb2 = bitsy.request("heartbeat")

		#
		# The 'standard' divide by n clock divider
		#
		counter = Signal(24)
		ticks = int((500e6/(blink_freq * bitsy.default_clk_period))) - 1

		self.sync += [
			hb.eq(~hb),	# this should clock at the 1/2 SYSCLK
			counter.eq(counter + 1),
			If(counter == ticks,
				If(count == 0x99,
					count.eq(0)
				).Elif(count[:4] == 9,
					count.eq(count + 7)
				).Else(
					count.eq(count + 1)
				)
			),
		]
		self.comb += [ hb2.eq(~hb) ]

#
# Now instantiate a counter, which instantiates an LED display
# sub-module which is showing the count.
#
count_module = Counter(10);

#
# And "build" this into a bit file
#

bitsy.build(count_module)

