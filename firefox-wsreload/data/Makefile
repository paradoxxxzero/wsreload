# Batch convert SVG files in a set of PNG images in different sizes
# This makefile uses the inkscape command line mode to export
# SVG files in a set of foo-{SIZES}.png images
# Cristian Martinez
all: icons

# Input SVG images without extensions
IMAGES   = icon icon_inactive
# Output PNG sizes
SIZES	   = 16 32 48 64
INKSCAPE = inkscape
DASH     = -

INPUTS   := $(foreach icon, $(IMAGES), $(icon).svg)
OUTPUTS  := $(patsubst %.svg, %, $(INPUTS))
SUFFIXES := $(foreach size, $(SIZES), $(DASH)$(size).png)
OUTPUTS  := $(foreach img, $(OUTPUTS), $(addprefix $(img),$(SUFFIXES))) 

icons: $(OUTPUTS) .FORCE

%.png:
	@echo "# creating $@"
	@$(INKSCAPE) --export-png $@ -w $(lastword  $(subst $(DASH),.svg ,$*)) \
	                                $(firstword $(subst $(DASH),.svg ,$*))

clean:
	@rm -f $(OUTPUTS)
	@echo "all files have been removed"
	
.FORCE:
