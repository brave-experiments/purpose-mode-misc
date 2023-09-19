base_name = toggles-over-time
csv = $(base_name).csv
r_script = $(base_name).R
tikz_plot = $(base_name).tex

preview_input = plot.tex
preview_output = plot.pdf

all: $(tikz_plot)

.PHONY: preview
preview: $(preview_output)

$(preview_output): $(preview_input) $(tikz_plot)
	xelatex $(preview_input)

$(tikz_plot): $(csv) $(r_script) Makefile
	Rscript $(r_script) $(csv)
	cat $(tikz_plot) | \
		sed 's/toggles-over-time_ras1/plots\/toggles-over-time_ras1/' | \
		pbcopy

.PHONY: clean
clean:
	rm -f $(tikz_plot) $(preview_output) Rplots.pdf
