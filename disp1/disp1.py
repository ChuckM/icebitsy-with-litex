#!/usr/bin/env python3
#
# Written by Chuck McManis September, 2021
# still just easy stuff
#
# Slowly developing a standard set of imports for a 
# given platform
#
from migen import *
from litex.build.generic_platform import *
from litex_boards.platforms.icebreaker_bitsy import Platform
# we'll call it a bitsy of type Platform()
bitsy = Platform()

# this is a pre-defined definition for seven segment displays from
# 1bitsquared
#from onebitsquared.pmod import led7seg

#
# Two steps in the design process here, one is some code to describe
# how the Digilent PMODs are connected, the other is the actual
# LED Chaser code.
#
# Step 1: Define the Digilent PMOD
#
# This is fairly simple code to express a Digilent LED8 PMOD connected
# to one of the icebreaker's PMOD ports. (PMOD1A, PMOD1B, PMOD2)
#
# Once added to the platform as an extension, you can access the
# individual LEDs as <name>.led0 thru <name>.led7.
#
def led7seg_pmod(pmod_port):
	return [
		("leddisplay", 0,
			Subsignal("seg_a", Pins(f"{pmod_port}:0")),
			Subsignal("seg_b", Pins(f"{pmod_port}:1")),
			Subsignal("seg_c", Pins(f"{pmod_port}:2")),
			Subsignal("seg_d", Pins(f"{pmod_port}:3")),
			Subsignal("seg_e", Pins(f"{pmod_port}:4")),
			Subsignal("seg_f", Pins(f"{pmod_port}:5")),
			Subsignal("seg_g", Pins(f"{pmod_port}:6")),
			Subsignal("sel", Pins(f"{pmod_port}:7")),
		)
	]

#
# Two LED8 Pmods are attached, one to PMOD1A and one to PMOD1B
#
bitsy.add_extension(led7seg_pmod("PMOD1"));
#platform.add_extension(led8_pmod("PMOD2"));

#
# Step 2: Define a module that is a "Chaser" (basically a set of leds
# that blink in sequence.  Like example 1 the counter/divider set up
# is used to provide a slower clock source. 
# 
# This code uses the PMODs that were added as extensions above.
#
class Chaser(Module):
	def __init__(self, blink_freq, sys_clk_freq):
		leds = bitsy.request("leddisplay")
#		more_leds = platform.request("led8")
		# note: they have a reset value of '1'
		digit = Cat(
			leds.seg_g, leds.seg_f, leds.seg_e, leds.seg_d, leds.seg_c,
			leds.seg_b, leds.seg_a)
#		glyphs = {
#			0 : digit.eq(~0b1111110), 
#			1 : digit.eq(~0b0110000),
#			2 : digit.eq(~0b1101101), 
#	    	3 : digit.eq(~0b1111001),
#			4 : digit.eq(~0b0110011),
#			5 : digit.eq(~0b1011011),
#	    	6 : digit.eq(~0b1011111),
#        	7 : digit.eq(~0b1110000),
#        	8 : digit.eq(~0b1111111),
#        	9 : digit.eq(~0b1110011) }
		foo = (
			C(~0b1111110),  # 0
			C(~0b0110000),	# 1
			C(~0b1101101),	# 2
			C(~0b1111001),	# 3
			C(~0b0110011),	# 4
			C(~0b1011011),	# 5
			C(~0b1011111),	# 6
			C(~0b1110000),	# 7
			C(~0b1111111),	# 8
			C(~0b1110011),	# 9
			C(~0b1110111),	# A
			C(~0b0011111),	# b
			C(~0b1001110),	# c
			C(~0b0111101),	# d
			C(~0b1001111),	# E
			C(~0b1000111),	# F
		)
		glyphs = Array(foo)
		num = Signal(7) 
		select = Signal(1, reset=0)
		count = Signal(8)

		# this makes a 32 bit counter
		counter = Signal(32)
		self.sync += [
			counter.eq(counter + 1),
			If(counter == int((sys_clk_freq/blink_freq)/2 -1),
				counter.eq(0),
				#
				# Display a digit on one of the displays
				#
				If(num > 15, num.eq(0)
				).Else(num.eq(num + 1)),
				digit.eq(glyphs[num]),
#				Case(num, glyphs),
				leds.sel.eq(1),
			)
		]
		self.comb += []

#
# now we are going to instantiate our LED chaser running
# at 10Hz.
#
led_module = Chaser(3, 12e6);

#
# And "build" this into a bit file
#

bitsy.build(led_module)

