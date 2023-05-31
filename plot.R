#!/usr/bin/env Rscript
library(optparse)
library(cvms)
library(dplyr)
library(ggplot2)

option_list <- list(
    make_option(c("--data_path"),
        type = "character",
        help = "Path to data file (.csv)."
    ),
    make_option(c("--out_path"),
        type = "character",
        help = "Path to save confusion matrix plot at."
    ),
    make_option(c("--data_are_counts"),
        action = "store_true", default = FALSE,
        help = "Indicates that `--data_path` contains counts, not predictions."
    ),
    make_option(c("--target_col"),
        type = "character",
        help = "Target column"
    ),
    make_option(c("--prediction_col"),
        type = "character",
        help = "Prediction column"
    ),
    make_option(c("--n_col"),
        type = "character",
        help = "Count column (when `--data_are_counts`)."
    ),
    make_option(c("--classes"),
        type = "character",
        help = "Comma-separated class names. Only these classes will be used - in the specified order."
    ),
    make_option(c("--prob_of_class"),
        type = "character",
        help = "Name of class that probabilities are of."
    ),
    make_option(c("--palette"),
        type = "character",
        help = "Color palette."
    ),
    make_option(c("--width"),
        type = "integer",
        help = "Width of plot in pixels."
    ),
    make_option(c("--height"),
        type = "integer",
        help = "Height of plot in pixels."
    ),
    make_option(c("--dpi"),
        type = "integer",
        help = "DPI of plot."
    ),
    make_option(c("--add_sums"),
        action = "store_true", default = FALSE,
        help = "Wether to add sum tiles."
    ),
    make_option(c("--add_counts"),
        action = "store_true", default = FALSE,
        help = "Wether to add counts."
    ),
    make_option(c("--add_normalized"),
        action = "store_true", default = FALSE,
        help = "Wether to add normalized counts (i.e. percentages)."
    ),
    make_option(c("--add_row_percentages"),
        action = "store_true", default = FALSE,
        help = "Wether to add row percentages."
    ),
    make_option(c("--add_col_percentages"),
        action = "store_true", default = FALSE,
        help = "Wether to add column percentages."
    ),
    make_option(c("--add_zero_percentages"),
        action = "store_true", default = FALSE,
        help = "Wether to add percentages to zero-tiles."
    ),
    make_option(c("--add_zero_text"),
        action = "store_true", default = FALSE,
        help = "Wether to add text to zero-tiles."
    ),
    make_option(c("--add_zero_shading"),
        action = "store_true", default = FALSE,
        help = "Wether to add shading to zero-tiles."
    ),
    make_option(c("--add_arrows"),
        action = "store_true", default = FALSE,
        help = "Wether to add arrows to row/sum percentages. Requires additional packages."
    ),
    make_option(c("--counts_on_top"),
        action = "store_true", default = FALSE,
        help = "Wether to have the counts on top and normalized counts below."
    ),
    make_option(c("--diag_percentages_only"),
        action = "store_true", default = FALSE,
        help = "Wether to only show diagonal row/column percentages."
    ),
    make_option(c("--digits"),
        type = "integer",
        help = "Number of digits to show for percentages."
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

print(opt)

data_are_counts <- opt$data_are_counts

# read.csv turns white space into dots
target_col <- stringr::str_squish(opt$target_col)
target_col <- stringr::str_replace_all(target_col, " ", ".")
prediction_col <- stringr::str_squish(opt$prediction_col)
prediction_col <- stringr::str_replace_all(prediction_col, " ", ".")

n_col <- NULL
if (!is.null(opt$n_col)) {
    n_col <- stringr::str_squish(opt$n_col)
    n_col <- stringr::str_replace_all(n_col, " ", ".")
}

# Read and prepare data frame
df <- tryCatch(
    {
        read.csv(opt$data_path)
    },
    error = function(e) {
        print(paste0("Failed to read data from ", opt$data_path))
        print(e)
        stop(e)
    }
)
print(df)

df <- dplyr::as_tibble(df)
print(df)
df[[target_col]] <- as.character(df[[target_col]])

if (isTRUE(data_are_counts)) {
    df[[prediction_col]] <- as.character(df[[prediction_col]])
}

# Predictions can be either probabilities or
# hard class predictions
if (is.integer(df[[prediction_col]]) || !is.numeric(df[[prediction_col]])) {
    all_present_classes <- sort(
        c(
            unique(df[[target_col]]),
            unique(df[[prediction_col]])
        )
    )
} else {
    all_present_classes <- sort(
        unique(df[[target_col]])
    )
}


if (!is.null(opt$classes)) {
    classes <- as.character(
        unlist(strsplit(opt$classes, "[,:]")),
        recursive = TRUE
    )
} else {
    classes <- all_present_classes
}
print(paste0("Selected Classes: ", paste0(classes, collapse = ", ")))

if (!isTRUE(data_are_counts)) {
    # We remove the unwanted classes from the confusion matrix
    # (easier - possibly slower in edge cases)
    family <- ifelse(length(all_present_classes) == 2, "binomial", "multinomial")
    print(df)

    # TODO : use prob_of_class to ensure probabilities are interpreted correctly!!
    # Might need to invert them to get it to work!
    evaluation <- tryCatch(
        {
            cvms::evaluate(
                data = df,
                target_col = target_col,
                prediction_cols = prediction_col,
                type = family,
            )
        },
        error = function(e) {
            print("Failed to evaluate data.")
            print(head(df, 5))
            print(e)
            stop(e)
        }
    )

    confusion_matrix <- evaluation[["Confusion Matrix"]][[1]]
} else {
    confusion_matrix <- dplyr::rename(
        df,
        Target = !!target_col,
        Prediction = !!prediction_col,
        N = !!n_col
    )
}

confusion_matrix <- dplyr::filter(
    confusion_matrix,
    Prediction %in% classes,
    Target %in% classes
)


confusion_matrix_plot <- tryCatch(
    {
        cvms::plot_confusion_matrix(
            confusion_matrix,
            class_order = classes,
            add_sums = opt$add_sums,
            add_counts = opt$add_counts,
            add_normalized = opt$add_normalized,
            add_row_percentages = opt$add_row_percentages,
            add_col_percentages = opt$add_col_percentages,
            rm_zero_percentages = !opt$add_zero_percentages,
            rm_zero_text = !opt$add_zero_text,
            add_zero_shading = opt$add_zero_shading,
            add_arrows = opt$add_arrows,
            counts_on_top = opt$counts_on_top,
            diag_percentages_only = opt$diag_percentages_only,
            digits = as.integer(opt$digits),
            palette = opt$palette
        )
    },
    error = function(e) {
        print("Failed to create plot from confusion matrix.")
        print(confusion_matrix)
        print(e)
        stop(e)
    }
)

tryCatch(
    {
        ggplot2::ggsave(
            opt$out_path,
            width = opt$width,
            height = opt$height,
            dpi = opt$dpi,
            units = "px"
        )
    },
    error = function(e) {
        print(paste0("Failed to ggsave plot to: ", opt$out_path))
        print(e)
        stop(e)
    }
)
