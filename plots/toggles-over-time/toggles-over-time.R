require(ggplot2)
require(tikzDevice)
require(scales)

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
data <- read.csv(input_file, header = TRUE)

tikz(
      file = "toggles-over-time.tex",
      standAlone = FALSE,
      width = 2.5,
      height = 1.5
)

ggplot(data, aes(
      x = day,
      y = pid,
      fill = num_toggles
)) +
      geom_tile(color = "light gray") +
      geom_text(aes(label = num_toggles), color = "#555555", size = 3) +
      theme_minimal() +
      scale_fill_gradient(
            low = "white",
            high = "red"
      ) +
      theme(
            axis.title.y = element_blank(),
            legend.position = "none",
            panel.grid.major = element_blank(),
      ) +
      labs(
            fill = "Number of toggles",
            x = "Day of intervention phase",
      )

dev.off()
