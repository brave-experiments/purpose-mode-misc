require(ggplot2)
require(tikzDevice)
require(scales)

args <- commandArgs(trailingOnly = TRUE)
input_file <- args[1]
data <- read.csv(input_file, header = TRUE)

tikz(
      file = "toggles-per-participant.tex",
      standAlone = FALSE,
      width = 3.7,
      height = 2.3
)

ggplot(data, aes(
      y = pid,
      x = feature,
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
            axis.text.x = element_text(
                  angle = 90,
                  vjust = 0,
                  hjust = 1,
            ),
            axis.title.x = element_blank(),
            axis.title.y = element_blank(),
            legend.position = "none",
            panel.grid.major = element_blank(),
      ) +
      labs(fill = "Number of toggles")

dev.off()
