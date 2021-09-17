#!/usr/bin/env python3
#
# Super trivial litex example, to get a feel for the flow
# from using litex.
# 
# Written by Chuck McManis August, 2021
# Not a lot of useful stuff here feel free to use it how you would like.
#
# Step one, import all the things from Migen ...
#
from migen import *

# Step two, import the base Platform class from Litex
from litex.build.generic_platform import *

# Step three, import a 'build flow' for the FPGA on the platform.
# In the case of the icebitsy it is a Lattice ICE40KUP5 so we import
# "Lattice" build flow which uses the YosysHQ tools.
from litex.build.lattice import LatticePlatform

#
# Step four here is building a "platform" (note that Litex-boards already
# has a definition for this board, but I wanted to see what was inside
# the derivative platform class)
# 
# First up is Input / Output
#
# This is an array of defines which tell Litex things about the board.
# In this case, the clock line, two user controllable LEDs, and a
# user accessible push button. In an HDL flow this would be like the
# user constraints file, but in Litex it is an array of I/Os in an
# array cleverly named "_io"
#
# Each tuple in this list defines a 'Signal()' which is the Migen class
# that wires things together. The first element of this tuple is a user
# defined name which you can use later to "wire up" this signal to your
# design. The second element is how many (zero based) of these there are.
#
# What that means is that you can define both LEDs that are part of the
# board as "user_led" but one would be number '0' and one would be number
# '1'. However, in my platform file I'm identifying them by their color (red
# or green) because that is an easier way to get the "correct" one.
#
# The third element of this tuple are the "pin" (or pins) associated with
# this I/O. It is defined by the Migen 'Pin()' function.
#
# If there is more than one pin associated with an I/O then its
# 'shape' is size 'n' (based on the number of pins). If you look at the
# board definition provided by the litex-boards repo you can see that
# a pin can also be a 'SubSignal' which allows you to refer to elements
# by name. I use this capability in the cylon example.
#
# The last element of this tuple are the IO Voltage levels, these are
# predefined by Migen, so in our case LVCMOS33 is a 3.3V low voltage
# CMOS pin.
#
#
_io = [
	# Clock (which is 12 MHz on the standard board)
	("clk12mhz", 0, Pins("35"), IOStandard("LVCMOS33")),

	# LEDs on the Icebitsy board.
	# One is red, and one is green.
	("user_led_red", 0, Pins("25"), IOStandard("LVCMOS33")),
	("user_led_green", 0, Pins("6"), IOStandard("LVCMOS33")),

	# You could also define them as a 2 bit wide signal thusly
	("user_leds", 0, Pins("25 6"), IOStandard("LVCMOS33")),
	
	# The "user" button. 
	("user_button", 0, Pins("2"), IOStandard("LVCMOS33")),
]

#
# Now that we have the I/Os defined we can construct a subclass
# of the Litex Platform class for this board.
#
# We subclass "LatticePlatform" because it has the build flow for the
# Lattice FPGA we are using, so the class hierarchy is
# 		Platform-> LatticePlatform -> Icebitsy
#
#
class Icebitsy(LatticePlatform):
	"""
		Chuck's platform definition for the Icebitsy, it is incomplete.
		use the litex-boards.platforms.icebreaker_bitsy for your real
		code.
	"""
	# Set some defaults.
	# These are taken from the other platforms that Litex defined but you
	# could add your own as well. It isn't clear what "must" be here and
	# what is optional. 
	#
	# This variable holds the name of the system clock pin, note that
	# is defined which pad this is in the _io list.
	#
	default_clk_name = "clk12mhz"

	#
	# Set the period in nanoseconds. It is interesting to note that
	# defining it this way means it is a floating point value
	#
	default_clk_period = 1e9/12e6

	#
	# And the instantiation method, where we tell it to use the "icestorm"
	# toolchain (this is the YosysHQ tool chain with nextpnr, Etc.), and
	# the specific Lattice FPGA we are using and its package (which affects
	# mapping pin numbers to FPGA I/Os.
	#
	def __init__(self, toolchain="icestorm"):
		LatticePlatform.__init__(self, "ice40-up5k-sg48", _io, 
														toolchain=toolchain)
#	The litex platforms include this do_finalize method but I'm not really
#	sure who calls them or for what reason. It adds a constraint for 
#	timing analysis. Sadly it 
#
	def do_finalize(self, fragment):
		LatticePlatform.do_finalize(self, fragment)
		self.add_period_constraint(self.lookup_request("clk12mhz", loose=True),
 												Icebitsy.default_clk_period)

#
# And now the "design" (sort of like the 'behavioural' clause of VHDL)
#
# First off create a Platform instance ...
#
platform = Icebitsy()

#
# Now we define a module that is a "blinker" (basically an LED, a
# counter/divider, and a clock source). We'll see later that this is
# also the "top" module that you would create if you were using an HDL
# tool like Quartus or Vivado.
#
# The interesting thing for me is that all of the heavy lifting goes
# on in the __init__ method. This defines the modules "wires" which
# are the equivalent in Verilog or VHDL as the module's inputs and
# outputs. 
#
# UNLIKE HDL, the clock domain here is implicit rather than being
# explicit. All modules are presumed to be connected to the default
# clock of the plaform and that is the clock that drives the
# 'sync' blocks. We "request" the LED resources
# and in this case we ask for them both.
#
# It is possible to create additional clock domains but that is not
# needed for this simple example.
#
class Blink(Module):
	"""
		Blink the USER leds on the Icebitsy
	"""
	def __init__(self, blink_freq):
		#
		# Now we "request", which is equivalent to fetching the constraints
		# for, the two LEDs on this platform.
		#
		red_led = platform.request("user_led_red")
		green_led = platform.request("user_led_green")
		
		#
		# Grab the user button as a signal.
		#
		button = platform.request("user_button")

		# 
		# To create a delay, we need a "divide-by-n" counter, and we're going
		# to pass in the desired blink frequency when we instantiate this
		# module. Since the clock rate is 12 MHz, and we'll not really want
		# to go any slower than, say half a hertz, we can use a 24 bit counter.
		#
		counter = Signal(24)

		#
		# This is an example of how you can use python to do some grunt work
		# for you. (there are better examples later). Basically calculate
		# how many 'ticks' are in one half period of the blink frequency.
		#
		# Since period is in nanoseconds, The delay in 'ticks' would be 
		# (((1e9 * 1/blink_freq) / period) / 2) - 1
		#             \              \       \    \--- zero based period
		#              \              \       \------- half the period 
		#               \              \-------------- period in ns
		#                \---------------------------- The blink period in ns
		#
		# As a simplification 1e9 / 2 is 500e6 (a bit of algebra)
		# 
		ticks = int(500e6 / (blink_freq * platform.default_clk_period)) - 1

		#
		# This code is the "synchronous" stuff going on in the FPGA
		# (aka clock driven) and so it lives in the instance list
		# named 'sync'. The contents of the list consist of a series
		# of Migen FHDL statements that are implemented inside a
		# "when positive edge of the clock, do ..." kind of block.
		#
		self.sync += [
			# in FHDL we use .eq() on a signal to assign it a value.
			# In this case we are incrementing the counter by 1. This
			# happens on every clock cycle, so 12 million times a second.
			counter.eq(counter + 1),
			# the next statement is an "if" statement. The way this works
			# is if the condition (first argument) evaluates to 'true' then
			# the statements that follow should be executed. 
			#
			# The condition checks to see if the count is equal to 1/2 the
			# number of clock ticks in the blink frequency. Note that this
			# is statically computed, this module doesn't vary its blink
			# speed once instantiated.
			If(counter == ticks,
				# when true, the counter is reset to 0 and the red LED is
				# toggled to it's alternate state
				counter.eq(0),
				red_led.eq(~red_led),
			)
			# and that is all there is to it, the LED blinks at 'blink_rate'
		]
		#
		# And this code is all "combinatorial" logic so is essentially
		# wiring from point A to point B kinds of things with optional
		# boolean logic / muxing what not going on that doesn't require
		# registers.
		#
		self.comb += [
				# Now we could have created a registered bit for
				# the green LED state, but that wouldn't demonstrate
				# the comb list.
				#
				# Instead, we create two behaviors, one where green is the
				# complement of red, and one where green is the same as red.
				# We control which choice is taken based on the state of the
				# user push button.
				# 
				If(button == 1,
					green_led.eq(~red_led)
				).Else(
					green_led.eq(red_led)),
		]

#
# So this bit of code instantiates the Blink module.
#
led_module = Blink(3);

#
# And finally, we "build" it which takes the module structure as defined
# and combines it with the platform to synthesize a design. The output
# of the build stream is a bit file that we can load into the board
# (see the makefile)
#

platform.build(led_module)

