Simple Four Digit LED Display
----------------------------

In the previous examples we used the `SevenSegmentLedDisplay` module to
display the output of an 8 bit binary coded decimal (BCD) count. In this
example we just extend that to an additional display to demonstrate how
easy it is once you have this stuff in modules to put other stuff together.

In this example we use two instances of the `SevenSegmentLedDisplay` module
and make our BCD counter 16 bits (for four decimal digits). It is otherwise
nearly identical to the previous example.

There are also some shennanigans in the `Makefile` which basically create a
symlink to led7segment.py from its "home" in the pmod directory. Versions of
pmod modules in the pmod directory are the "canonical" ones and it saves on
keeping copies in all of the directories up to date.
