#!/usr/bin/env python3
#
# Super trivial litex example, to get a feel for the flow
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

# Our IceBreaker is based on the Lattice ICE40UP5K FPGA chip
from litex.build.lattice import LatticePlatform

#
# Input / Output
#
# This is an array of defines which tell Litex things about the board.
# In this case, the clock line, two user controllable LEDs, and a
# user accessible push button.
#
# This is essentially binding the "name" to a pin, and telling Litex
# what sort of I/O levels to use. LVCMOS33 is 3.3V I/O with LVCMOS levels
# for '1', and '0'. Other choices would be things like LVTTL for low voltage
# TTL.
#
_io = [
	# Clock
	("clk12", 0, Pins("35"), IOStandard("LVCMOS33")),

	# LEDs on the main Icebreaker board (not the break off PMOD)
	("user_led_red", 0, Pins("25"), IOStandard("LVCMOS33")),
	("user_led_green", 1, Pins("6"), IOStandard("LVCMOS33")),
	
	# Button
	("user_button", 0, Pins("2"), IOStandard("LVCMOS33")),
]

#
# The "platform"
#
# This module defines the board we're using and more importantly the
# specific FPGA and package we are using. Pin numbers are specific to
# packages so it is important to get this correct.
#
class Platform(LatticePlatform):
	default_clk_name = "clk12"
	default_clk_period = 1e9/12e6 # period is in nanoseconds here

	def __init__(self, toolchain="icestorm"):
		LatticePlatform.__init__(self, "ice40-up5k-sg48", _io, 
														toolchain=toolchain)
	def do_finalize(self, fragment):
		LatticePlatform.do_finalize(self, fragment)
		self.add_period_constraint(self.lookup_request("clk12", loose=True),
													1e9/12e6)

#
# And now the "design" (sort of like the 'behavioural' clause of VHDL)
#
# First off create a Platform instance ...
#
platform = Platform()

#
# Now we define a module that is a "blinker" (basically an LED, a
# counter/divider, and a clock source). We "request" the LED resources
# and in this case we ask for them both.
#
class Blink(Module):
	def __init__(self, blink_freq, sys_clk_freq):
		red_led = platform.request("user_led_red");
		green_led = platform.request("user_led_green");
		# this makes a 32 bit counter
		counter = Signal(32);
		self.sync += [
			counter.eq(counter + 1),
			If(counter == int((sys_clk_freq/blink_freq)/2 -1),
				counter.eq(0),
				red_led.eq(~red_led),
			)
		]
		self.comb += [
				# green LED is "opposite" of the red LED always
				green_led.eq(~red_led),
		]

#
# now we are going to instantiate our blinker, to be tricky
# we're going to actually make two of them, one for the RED
# LED and one for the Green LED.
#
# In the next example we're going to see about having two modules
# load at the same time.
#
led_module = Blink(3, 12e6);

#
# And "build" this into a bit file
#

platform.build(led_module)

