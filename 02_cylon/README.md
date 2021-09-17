New features, new module
------------------------

Now that we've proven the toolchain works, this example goes on to
use some more features of LiteX.

The first thing is that this example changes is that it uses the 
'built in' platform definition for the 1Bitsquared Icebitsy board.
That means less typing in our code and, in theory, it would track
versions of the Icebitsy as they were released. It also means that
all the pins are already defined so we don't have to define them. It
also uses a new construct class `Connector` to describe the three
PMOD ports (1, 2, and 3). 

The second thing this example does is to programmatically define the signals
of a PMOD, in this case the 
[Digilent 8 LED PMOD](https://store.digilentinc.com/pmod-8ld-eight-high-brightness-leds/).

The code in `gen_led8` takes two arguments, the connector that the PMOD
is plugged into and the instance number. Since we are using two we use
this function twice, once for the PMOD connected to PMOD1 and once for
the PMOD connected to PMOD2.

That is followed by a call to `icebitsy.add_extension()` which adds those
PMOD signal resources to our design.

And finally our simple design module, called `Cylon` expects that these LED8
PMODs are present, and it finds them using `icebitsy.request("led8")` which
it does twice, to get access to the signal definitions for both PMODs.

Another feature of this example is that it creates a bus named, `all_leds`,
using the `Cat(...)` class, that defines a bus of all 16 leds as a single
16 wire bus.

The module defines `display` which holds the state of 16 LEDs in it, and
because it is assigned in the `sync` block it will become a register. There
is also a 1 bit flip flop assigned to the value `direction` to indicate if
the chaser is moving left or right.

The same count down timer/divider is used to convert the clock in signal to
a clock at the frequency that the LED will change state.

In the combinatorial section, the value in the `display` register is routed
to the LED8 PMODs. This is done with an assignment much like the `Blink`
code in example `01_blink`  did but with more LEDs.

When writing this code I learned some importatant stuff about 
using `Signal(...)` and the names of wires. I've left in the code the three
different ways I tried to make this work. Two of them actually do what I
wanted and one does not.

