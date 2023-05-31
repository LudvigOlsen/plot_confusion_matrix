#!/usr/bin/env Rscript
library(optparse)
library(cvms)

option_list <- list(
    make_option(c("--out_path"), type="character", 
                help="Path to save data at."),
    make_option(c("--num_classes"), type="integer", 
                help="Number of classes."),
    make_option(c("--num_observations"), type="integer",
                help="Number of observations."),
    make_option(c("--seed"), type="integer",
                help="Number of observations.")
                
)
 
opt_parser <- OptionParser(option_list=option_list)
opt <- parse_args(opt_parser)

print(opt)

# Set seed if given
if (!is.null(opt$seed)){
    set.seed(opt$seed)
}

# Make fairly certain predictions
rcertain <- function(n) {
  (runif(n, min = 1, max = 100)^1.4) / 100
}

# Generate data
data <- cvms::multiclass_probability_tibble(
  num_classes=opt$num_classes,
  num_observations=opt$num_observations,
  apply_softmax = TRUE,
  FUN = rcertain,
  class_name = "c",
  add_predicted_classes = TRUE,
  add_targets = TRUE
) 

data <- data[, c("Predicted Class", "Target")]

# Write to disk
write.csv(data, file = opt$out_path, row.names=FALSE)