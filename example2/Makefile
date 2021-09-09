#
# build a led chaser design example using Litex/Migen
#
DESIGN=cylon

$(DESIGN).bit:	build/top.txt
	icepack $< $@

build/top.txt: $(DESIGN).py
	./$(DESIGN).py

$(DESIGN).bin: build/top.bin
	cp $< $@

flash: $(DESIGN).bin
	dfu-util --verbose -d 1d50:6146 -a 0 -R -D  $< 

clean:
	rm -rf build $(DESIGN).bit $(DESIGN).bin
