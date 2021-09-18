#
# Build a module and a sub-module
#
#
# Linux version of the DFU utility
#
PROG = dfu-util
#
# Windows version of the DFU utility.
# Use this if you're building this under WSL. 
#
#PROG = dfu-util-static.exe
DESIGN=display

$(DESIGN).bin:	build/top.bin
	cp $< $@

build/top.bin: $(DESIGN).py led7segment.py
	./$(DESIGN).py

flash: $(DESIGN).bin
	$(PROG) -d 1d50:6146 -a 0 -R -D $<

clean:
	rm -rf build $(DESIGN).bin
