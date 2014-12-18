library("MASS") # for exponential fit

f <- file("stdin")
open(f)
data <- read.table(f, header=FALSE, col.names=c("spacing"))

exp_fit <- fitdistr(data$spacing, "exponential")
cat("lambda\n")
cat(sprintf("%g\n", exp_fit$estimate[["rate"]]))
