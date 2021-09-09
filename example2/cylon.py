#!/usr/bin/env python3
#
# Another slightly less litex example, to get a feel for the flow
# from using litex.
#
# Written by Chuck McManis August, 2021
# Not a lot of useful stuff here feel free to use it how you would like.
#
# first import all the things from Migen ...
#
from migen import *

# base class is the Platform()
from litex.build.generic_platform import *

# It is a known board so import that instead
from icebreaker import Platform

#
# First off create a Platform instance from the imported icebreaker 
#
platform = Platform()

#
# Two steps in the design process here, one is some code to describe
# how the Digilent PMODs are connected, the other is the actual
# LED Chaser code.
#
# Step 1: Define the Digilent PMOD
#
# This is fairly simple code to express a Digilent LED8 PMOD connected
# to one of the icebreaker's PMOD ports. (PMOD1, PMOD2, PMOD3)
#
# Once added to the platform as an extension, you can access the
# individual LEDs as <name>.led0 thru <name>.led7.
#
def led8_pmod(pmod_port):
	return [
		("led8", 0,
			Subsignal("led0", Pins(f"{pmod_port}:0")),
			Subsignal("led1", Pins(f"{pmod_port}:1")),
			Subsignal("led2", Pins(f"{pmod_port}:2")),
			Subsignal("led3", Pins(f"{pmod_port}:3")),
			Subsignal("led4", Pins(f"{pmod_port}:4")),
			Subsignal("led5", Pins(f"{pmod_port}:5")),
			Subsignal("led6", Pins(f"{pmod_port}:6")),
			Subsignal("led7", Pins(f"{pmod_port}:7")),
		)
	]

#
# Two LED8 Pmods are attached, one to PMOD1A and one to PMOD1B
#
platform.add_extension(led8_pmod("PMOD1"));
platform.add_extension(led8_pmod("PMOD2"));

#
# Step 2: Define a module that is a "Chaser" (basically a set of leds
# that blink in sequence.  Like example 1 the counter/divider set up
# is used to provide a slower clock source. 
# 
# This code uses the PMODs that were added as extensions above.
#
class Chaser(Module):
	def __init__(self, blink_freq, sys_clk_freq):
		leds = platform.request("led8")
		more_leds = platform.request("led8")
		# note: they have a reset value of '1'
		display = Signal(16, reset=1)
		direction = Signal(1, reset=1)

#
# This uses the 'Cat()' (concatenate) construct, to create a new signal
# that is an amalgam of all the LEDs. This makes it easier to set them
# all at once in the comb section below.
#
		all_leds = Cat(
				leds.led0, leds.led1, leds.led2, leds.led3,
				leds.led4, leds.led5, leds.led6, leds.led7,
				more_leds.led0, more_leds.led1, more_leds.led2, more_leds.led3,
				more_leds.led4, more_leds.led5, more_leds.led6, more_leds.led7,
		)

		# this makes a 32 bit counter
		counter = Signal(32)
		self.sync += [
			counter.eq(counter + 1),
			If(counter == int((sys_clk_freq/blink_freq)/2 -1),
				counter.eq(0),
				#
				# This is the chaser code, it combines remembering
				# what direction the chaser is running, resetting the
				# display when it gets to the end, and then changing
				# the direction.
				#
				If(direction == 1,
					If (display == 0b1000000000000000,
						display.eq(0b0100000000000000),
						direction.eq(0),
					).Else(
						display.eq(display << 1)
					)
				).Else(
					If (display == 0b1,
						display.eq(0b10),
						direction.eq(1)
					).Else(
						display.eq(display >> 1)
					)
				)
			)
		]
		#
		# This is the combinarial code. All it does is insure that
		# the LEDs mirror the state of the display[0..16] signal.
		#
		self.comb += [
			( 
#			This doesn't work
#
#			leds.eq(display[0:8]),
#			more_leds.eq(display[8:16])
#
#			This works but is ugly
#
#			leds.led0.eq(display[0]),
#			leds.led1.eq(display[1]),
#			leds.led2.eq(display[2]),
#			leds.led3.eq(display[3]),
#			leds.led4.eq(display[4]),
#			leds.led5.eq(display[5]),
#			leds.led6.eq(display[6]),
#			leds.led7.eq(display[7]),
#			more_leds.led0.eq(display[8]),
#			more_leds.led1.eq(display[9]),
#			more_leds.led2.eq(display[10]),
#			more_leds.led3.eq(display[11]),
#			more_leds.led4.eq(display[12]),
#			more_leds.led5.eq(display[13]),
#			more_leds.led6.eq(display[14]),
#			more_leds.led7.eq(display[15]),
#
#			This works and is easier to read. 
#
			all_leds.eq(display)
			)
		]

#
# now we are going to instantiate our LED chaser running
# at 10Hz.
#
led_module = Chaser(10, 12e6);

#
# And "build" this into a bit file
#

platform.build(led_module)

