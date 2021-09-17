#!/usr/bin/env python3
#
# Written by Chuck McManis August, 2021
# Not a lot of useful stuff here feel free to use it how you would like.
#
# first import all the things from Migen ...
#
from migen import *

# base class is the Platform()
from litex.build.generic_platform import *

#
# Okay, so unlike in 01_Blink, this version just grabs the predefined
# platform from litex_boards.platform
#
from litex_boards.platforms.icebreaker_bitsy import Platform

#
# Create an instance of an icebitsy from it. This has the various LEDs
# and connectors pre-defined.
#
icebitsy = Platform()

#
# Using python to automate some typing.
#
# This function loops through 0 to 7 and defines Subsignals of the form
# "led<n>", "PMODx:<n>".
#
# Two interesting things going on here, Subsignals and Connections.
#
# Subsignal(...) gives a name to one or more of the signals that are part of a
# Signal(...) definition. If you look in the platform definition for the
# icebitsy you will see there is a definition of 'serial' with two sub-signals
# one called 'rx' and one called 'tx'. This creates a new signal called 'led8'
# which has 8 sub-signals led0 through led7.
#
# Connections(...) are I/O pins that go off board or to a connector. In this
# case there are three PMOD connectors, each has eight I/Os. In the platform
# definition file they are assigned to pins on the FPGA and named one of PMOD1
# PMOD2, or PMOD3. Unlike signals they are simply a text map from a connector
# name : pin number (0 - n) to the string to give to the Pin(...) class that
# connects that to the FPGA proper. So PMOD3:0 is pin 0, of connector PMOD3.
#
# The net effect of this code is to generate an 8 bit wide signal with each
# line of that signal having its own subname. They are then used in module
# code with something like "<SignalName>.led0" to talk to the first LED.
#
def gen_led8(pmod_port, num):
	led8 = ["led8", num]
	for i in range(8):
		led8.append(
			Subsignal(f"led{i}", Pins(f"{pmod_port}:{i}"),
								 IOStandard("LVCMOS33")))
	return tuple(led8)

#
# Two LED8 Pmods are attached, one to PMOD1 and one to PMOD2.
# The gen_led8 code creates a tuple that defines an "extension." Module
# code can then request that extension from the platform later and that
# is what we do in this code. We add a different unit number to them so
# that we can pick which one we want to wire up in our module code.
#
icebitsy.add_extension([gen_led8("PMOD1", 0)])
icebitsy.add_extension([gen_led8("PMOD2", 1)])

#
# At this point we have an augmented platform with extensions describing
# the connection to two LED8 PMODs. At this point then we define a top
# level module like we did in Blink to send some data to them.
#
# If you don't understand why it's called 'Cylon' look up Battlestar
# Galactica on the Internet :-). I suppose I could also name it Night Rider
# but that is more typing.
#
class Cylon(Module):
	"""
		A module that has an LED bouncing back and forth on two LED8
		PMODs connected to PMOD port 1 and PMOD port 2
	"""

	def __init__(self, blink_freq):
		#
		# As with the Blink example, we "request" the signals associated
		# with the name "led8" because we're going to be talking to them.
		#
		leds = icebitsy.request("led8", 0)
		more_leds = icebitsy.request("led8", 1)
		#
		# Now we define a 'display' register which will hold the state
		# of 16 LEDs and we add the parameter 'reset=1' which means that
		# the reset state will set the value to 0b0000000000000001
		display = Signal(16, reset=1)

		#
		# Direction remembers if we are going left or right.
		#
		direction = Signal(1)

		#
		# Same counter/ticks like we used in Blink, look at the comments
		# in that code for why 24 is enough bits of counter or how we
		# compute ticks.
		counter = Signal(24)
		ticks = int(500e6 / (blink_freq * icebitsy.default_clk_period)) - 1


		#
		# And this is a contrived example (in a planned example they would have
		# been defined this way) but it demonstrates an FHDL function i
		# 'Cat(...)' which is short for concatenate.
		#
		# This code is essentially punning (symlinking?) the 16 leds in the
		# two LED8 PMODs into a single bus called "all_leds" which has a 'shape'
		# of 16. What that means is we can assign a 16 bit value to this bus
		# and it will change all of the LEDs at once. (We don't need to turn
		# each one on individually). Now this example is just adding them in
		# order, but the nice thing here is that you could combine a bunch of
		# signals into a single bus for easier assignment or reading.
		#
		all_leds = Cat(
				leds.led0, leds.led1, leds.led2, leds.led3,
				leds.led4, leds.led5, leds.led6, leds.led7,
				more_leds.led0, more_leds.led1, more_leds.led2, more_leds.led3,
				more_leds.led4, more_leds.led5, more_leds.led6, more_leds.led7,
		)

		#
		# Now for the synchronous part.
		#
		# When enough ticks have gone by (the If() statement) the code does
		# the following:
		#
		#	if the direction is LEFT then
		#		if the display is 0b1000...0 then
		#			set the direction to RIGHT
		#		else
		#			rotate the display one bit left
		#	else
		#		if the display is 0b000...1 then
		#			set the direction to LEFT
		#		else
		#			rotate the display one bit right
		#
		# Many will immediately recognize that this is the algorithm for
		# having a light ping pong from one end of a string of lights to
		# the other.
		#
		self.sync += [
			counter.eq(counter + 1),
			If(counter == ticks,
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
		# This is the combinatorial code. 
		# This code sends the state of the display register to
		# all 16 LEDs.
		# 
		#
		self.comb += [
			( 
			#
			# While writing this code I learned of several things that
			# didn't work in Migen/FHDL. I've left them in so that you
			# can see what my guesses looked like.
			#
			# This doesn't work, it was my first attempt. Remember how I
			# named all of those subsignals so that I could refer to
			# individual LEDs? Given that definition there is no way to
			# assign to all of them.
			#
			# Now you could define the entire PMOD port as an 8 bit signal.
			# That would work and you could refer to individual pins with
			# the : syntax. However I wanted to have 'named' leds.
			#
#			leds.eq(display[0:8]),
#			more_leds.eq(display[8:16])
			#
			# This does work but it is ugly and a lot of typing!
			#
			# Each LED is individually addressed and it pulls from one
			# bit of the display register
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
			# This works AND it is easier to read.
			#
			# By building that concatenation, you can assign to
			# it all at once, and so that is what this does.
			#
			all_leds.eq(display)
			)
		]

#
# now we instantiate our LED chaser.
#
led_module = Cylon(25);

#
# And "build" this into a bit file
#
icebitsy.build(led_module)

