Getting Started with LiteX and Icebitsy
-----------------------------------------

FPGA work has gotten very interesting under the auspices of open source.
One of the systems that has come out of that is called
[LiteX](https://github.com/enjoy-digital/litex). It wraps another interesting
tool called [Migen](https://github.com/m-labs/migen) which uses Python as
a sort of scripting language for defining complex hardware.

One of the more amazing things I have done recently was to tell Litex to
build a computer on an FPGA board and boot it and then run a program 
written for that computer. This isn't a "new" capability, a friend of mine
did this exact thing in VHDL using the Xilinx tools in the 90's, but the
amount of learning that was necessary to get that to work with the Xilinx
stack and VHDL was really large, and usually way more investment than any
"experiementer" would want to invest. It also required the implementor to
have a good understanding of hardware synthesis, and how it works. Not
something a lot of hobbyists, especially mostly software hobbyists, would
have. So it was pretty much unobtanium as far as they were concerned.

LiteX brought that down to a level where pretty much anyone could do this
using pre-existing CPU architecture (RISC-V) and some canned board
definition files. With that kind of impact I felt it deserved a closer
look and something I should try to understand how it does what it does.

So here we are, with the experiments I've been running to figure this
stuff out.

To make use of this repository you will want to install LiteX (which
also installs Migen) and the open source tools for the Lattice FPGA
(nextpnr, yosys, Etc.) from 
[OSS CAD Suite](https://github.com/YosysHQ/oss-cad-suite-build/releases/tag/2021-08-21).

  * **Example 1:** Create a simple blinker
    This is the "are my tools installed?" test which
    one needs do to when you start exploring something. Typing
	`make flash` from the example1 directory should cause the
	code to be built and programmed into the icebreaker.

 * **Example 2:** Build an LED Chaser
	This is a bit more sophisticated where it adds a definition for
	the Digilent LED8 PMOD and uses it in the implementation of a
	LED Chaser.


