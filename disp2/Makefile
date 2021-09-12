#
# build a display module
#
DESIGN=disp2

$(DESIGN).bin:	build/top.bin
	cp $< $@

build/top.bin: $(DESIGN).py
	./$(DESIGN).py

flash: $(DESIGN).bin
	dfu-util-static.exe -d 1d50:6146 -a 0 -R -D $<

clean:
	rm -rf build $(DESIGN).bin
