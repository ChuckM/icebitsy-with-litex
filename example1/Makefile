#
# Blink the LED example using Litex/Migen
#
blinky.bit:	build/top.txt
	icepack $< $@

blinky.bin: build/top.bin
	cp $< $@

build/top.txt: blinky.py
	./blinky.py

flash: blinky.bin
	dfu-util -d 1d50:6146 -a 0 -D $< -R

clean:
	rm -rf build blinky.bit
