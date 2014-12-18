library("ggplot2")
library("ggthemes")

f <- file("stdin")
open(f)
data <- read.table(f, header=FALSE, col.names=c("spacing"))

png("plot-in-R.png")
ggplot(data, aes(x=spacing)) +
  geom_histogram(aes(y=..density..), colour="black", fill="blue", alpha=0.4) +
  theme_economist() + scale_colour_economist()
dev.off()
