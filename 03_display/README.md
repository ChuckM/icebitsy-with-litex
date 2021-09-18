Simple Two Digit LED Display
----------------------------

In the previous two examples we built a platform and built a module which
runs on that platform. Then we built a module that integrated a PMOD which
was connected over one of platform's connectors. 

In this example we create a separate module for a PMOD device, in this case
a two digit, seven segment, LED display. Then when we build the "top"
module for the platform we add our new seven segment display as a submodule.
This is how migen wires things together, top module, which has zero or more
submodules, which themselves can have zero or more submodules. 

Things to note, when we define the I/O for the PMOD board we have to
extract out and reverse seven of the eight the PMOD pins. We do that
by creating a string in python to feed to the `Pins(...)` class that
has those pins reversed from the platform's PMOD connector. 

Next, we set up an FHDL `Array(...)` of sixteen constants using the `C(...)`
syntax as an array of glyphs for setting which LEDs are on and which are
off when displaying the hexidecimal digits 0-F.

And finally, in our top module you set up the counter so that it is actually
a binary coded decimal (BCD) up counter so that the display will count from
0 - 99 and roll over.

