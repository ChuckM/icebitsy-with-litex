#
# This is a module definition for the 1BitSquared 7 segment display
# PMOD that has two 7 segment displays. Of course the PMOD port only
# has 8 GPIO lines so how does it work? Well pin 7 (the eight bit) controls
# which of the two displays are active. So to have "both" displays lit at
# the "same" time, you have to multiplex them and so that is what this
# module does.
#

#
# Note it is mostly a migen module not a part of Litex but we are attaching
# it to a Litex platform. Separating this is another exercise for later.
#
from migen import *
from litex.build.generic_platform import *

class SevenSegmentLedDisplay(Module):
	"""
		This is the 7 segment LED display module for the 1BitSquared
		7 segment display PMOD. I've got two versions so I make
		allowances for invoking either one. When you instantiate it
		you need to pass it the platform (type Platform()), the PMOD
		you are using (string), and an 8 wire Signal for the 'value'
		which is displayed on the display.
	"""

	#
	# This is a predefined constant array of segment states to produce
	# the digits 0 through 9 and approximations of the letters A-F
	#
	glyphs = Array((
		# segs:  abcdefg
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
		))

	def __init__(self, platform, pmod, value = Signal(8), rev="1.1"):
		pins = ""
		for i in range(6, -1, -1):
			pins += f"{pmod}:{i} "
		io_def = ("led7seg", 0,
				Subsignal("num", Pins(pins)),
				Subsignal("sel", Pins(f"{pmod}:7")),
		)
		platform.add_extension([io_def])
		disp = platform.request("led7seg")
		# the active display
		ad = Signal(1)
		refresh = Signal(24)
		
		# set a 250 Hz refresh rate
		ticks = int(500e6/(250 * platform.default_clk_period)) - 1
		#
		# So in the clocked part this code toggles the 'select'
		# line of the PMOD at 65 Hz
		#
		self.sync += [
			refresh.eq(refresh + 1),
			If(refresh == ticks,
				refresh.eq(0),
				ad.eq(~ad),
				disp.sel.eq(ad)
			),
#			If(ad,
#				disp.num.eq(SevenSegmentLedDisplay.glyphs[value[4:]]),
#			).Else(
#				disp.num.eq(SevenSegmentLedDisplay.glyphs[value[:4]])),
		]
		#
		# In the combinatorial part of the code we just put
		# the appropriate digit on which ever display is selected
		# by the select line.
		#
		self.comb += [
			If(ad,
				disp.num.eq(SevenSegmentLedDisplay.glyphs[value[4:]]),
			).Else(
				disp.num.eq(SevenSegmentLedDisplay.glyphs[value[:4]])),
		]
