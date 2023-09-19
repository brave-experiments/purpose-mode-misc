require(ggplot2)
require(tikzDevice)
require(scales)

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
data <- read.csv(input_file, header = TRUE)

mean(data$hamming_distance)

tikz(
      file = "toggles-overlap.tex",
      standAlone = FALSE,
      width = 3.25,
      height = 1.25
)

ggplot(data, aes(x = hamming_distance)) +
      geom_bar() +
      theme_minimal() +
      labs(x = "Hamming distance", y = "Count")

dev.off()
