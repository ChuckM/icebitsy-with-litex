Very Simple Blinker
---------------------

So this is the first thing I needed to figure out. What the relationship
between all of the moving bits with
[Litex](https://github.com/enjoy-digital/Litex),
[Migen](https://github.com/m-labs/migen), and the open source FGPA tools
at [YosysHQ](https://github.com/YosysHQ).

To be clear, Litex is pretty cool technology and very innovative. But it's 
documentation leaves a lot to be desired. As a result I've spent some time
just "trying things" to see how they work and engaging with other users
on the 1BitSquared Discord server and Liberia IRC channels.

One of that outcomes was that there is a pretty good reference for the Migen
"FHDL" language located at 
[https://m-labs.hk/migen/manual/](https://m-labs.hk/migen/manual/).

Another minor complication is that programming the icebitsy requires using
[dfu-util](http://dfu-util.sourceforge.net/) As a result you have to manually
hold down the 'user' button while resetting to put it into DFU mode. This
save having an extra chip on board (like it is for the icebreaker).

What this example does
----------------------

So at the end of the day this creates a simple clock divider to blink the two
LEDs on the icebitsy. How they blink (together or in alternating) is controlled
by whether or not the user button is pushed. It is a very simple example that
helped me figure out some of the relationships between parts. See the source
code for additional documentation in the comments.
