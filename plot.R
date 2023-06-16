#!/usr/bin/env Rscript
library(optparse)
suppressWarnings(suppressMessages(library(cvms)))
suppressWarnings(suppressMessages(library(dplyr)))
suppressWarnings(suppressMessages(library(ggplot2)))
suppressWarnings(suppressMessages(library(jsonlite)))

dev_mode <- FALSE

option_list <- list(
    make_option(c("--data_path"),
        type = "character",
        help = "Path to data file (.csv)."
    ),
    make_option(c("--out_path"),
        type = "character",
        help = "Path to save confusion matrix plot at."
    ),
    make_option(c("--settings_path"),
        type = "character",
        help = "Path to get design settings from. Should be a .json file."
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
    make_option(c("--sub_col"),
        type = "character",
        help = "Sub column (when `--data_are_counts`)."
    ),
    make_option(c("--classes"),
        type = "character",
        help = paste0(
            "Comma-separated class names. ",
            "Only these classes will be used - in the specified order."
        )
    )
)

opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

design_settings <- tryCatch(
    {
        read_json(path = opt$settings_path)
    },
    error = function(e) {
        print(paste0(
            "Failed to read design settings as a json file ",
            opt$settings_path
        ))
        print(e)
        stop(e)
    }
)

if (isTRUE(dev_mode)) {
    print("Arguments:")
    print(opt)
    print(design_settings)
}

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

sub_col <- NULL
if (!is.null(opt$sub_col)) {
    if (!data_are_counts) {
        stop("`sub_col` can only be specified when data are counts.")
    }
    sub_col <- stringr::str_squish(opt$sub_col)
    sub_col <- stringr::str_replace_all(sub_col, " ", ".")
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

df <- dplyr::as_tibble(df)

if (isTRUE(dev_mode)) {
    print(df)
}

if (!target_col %in% colnames(df)) {
    stop("Specified `target_col` not a column in the data.")
}
if (!prediction_col %in% colnames(df)) {
    stop("Specified `target_col` not a column in the data.")
}

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
    if (length(setdiff(classes, all_present_classes)) > 0) {
        stop("One or more specified classes are not in the data set.")
    }
} else {
    classes <- all_present_classes
}

if (isTRUE(dev_mode)) {
    print(paste0("Selected Classes: ", paste0(classes, collapse = ", ")))
}

if (!isTRUE(data_are_counts)) {
    # We remove the unwanted classes from the confusion matrix
    # (easier - possibly slower in edge cases)
    family <- ifelse(
        length(all_present_classes) == 2,
        "binomial",
        "multinomial"
    )

    evaluation <- tryCatch(
        {
            cvms::evaluate(
                data = df,
                target_col = target_col,
                prediction_cols = prediction_col,
                type = family
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

# Plotting settings

build_fontface <- function(bold, italic) {
    dplyr::case_when(
        isTRUE(bold) && isTRUE(italic) ~ "bold.italic",
        isTRUE(bold) ~ "bold",
        isTRUE(italic) ~ "italic",
        TRUE ~ "plain"
    )
}

top_font_args <- list(
    "size" = design_settings$font_top_size,
    "color" = design_settings$font_top_color,
    "fontface" = build_fontface(
        design_settings$font_top_bold,
        design_settings$font_top_italic
    ),
    "alpha" = design_settings$font_top_alpha
)

bottom_font_args <- list(
    "size" = design_settings$font_bottom_size,
    "color" = design_settings$font_bottom_color,
    "fontface" = build_fontface(
        design_settings$font_bottom_bold,
        design_settings$font_bottom_italic
    ),
    "alpha" = design_settings$font_bottom_alpha
)

percentages_font_args <- list(
    "size" = design_settings$font_percentage_size,
    "color" = design_settings$font_percentage_color,
    "fontface" = build_fontface(
        design_settings$font_percentage_bold,
        design_settings$font_percentage_italic
    ),
    "alpha" = design_settings$font_percentage_alpha,
    "prefix" = design_settings$font_percentage_prefix,
    "suffix" = design_settings$font_percentage_suffix
)

normalized_font_args <- list(
    "prefix" = design_settings$font_normalized_prefix,
    "suffix" = design_settings$font_normalized_suffix
)

counts_font_args <- list(
    "prefix" = design_settings$font_counts_prefix,
    "suffix" = design_settings$font_counts_suffix
)


if (isTRUE(design_settings$counts_on_top) ||
    !isTRUE(design_settings$show_normalized)) {
    # Counts on top!
    counts_font_args <- c(
        counts_font_args, top_font_args
    )
    normalized_font_args <- c(
        normalized_font_args, bottom_font_args
    )
} else {
    normalized_font_args <- c(
        normalized_font_args, top_font_args
    )
    counts_font_args <- c(
        counts_font_args, bottom_font_args
    )
}

tile_border_color <- NA
if (isTRUE(design_settings$show_tile_border)) {
    tile_border_color <- design_settings$tile_border_color
}

intensity_by <- tolower(design_settings$intensity_by)
if (grepl("normalized", intensity_by)) intensity_by <- "normalized"

palette <- design_settings$palette
if (isTRUE(design_settings$palette_use_custom)) {
    palette <- list(
        "low" = design_settings$palette_custom_low,
        "high" = design_settings$palette_custom_high
    )
}

# Sum tiles
sums_settings <- sum_tile_settings()
if (isTRUE(design_settings$show_sums)) {
    sums_settings <- sum_tile_settings(
        palette = design_settings$sum_tile_palette,
        label = design_settings$sum_tile_label,
        tile_border_color = tile_border_color,
        tile_border_size = design_settings$tile_border_size,
        tile_border_linetype = design_settings$tile_border_linetype
    )
}

confusion_matrix_plot <- tryCatch(
    {
        cvms::plot_confusion_matrix(
            confusion_matrix,
            sub_col = sub_col,
            class_order = classes,
            add_sums = design_settings$show_sums,
            add_counts = design_settings$show_counts,
            add_normalized = design_settings$show_normalized,
            add_row_percentages = design_settings$show_row_percentages,
            add_col_percentages = design_settings$show_col_percentages,
            rm_zero_percentages = !design_settings$show_zero_percentages,
            rm_zero_text = !design_settings$show_zero_text,
            add_zero_shading = design_settings$show_zero_shading,
            add_arrows = design_settings$show_arrows,
            arrow_size = design_settings$arrow_size,
            arrow_nudge_from_text = design_settings$arrow_nudge_from_text,
            intensity_by = intensity_by,
            darkness = design_settings$darkness,
            counts_on_top = design_settings$counts_on_top,
            place_x_axis_above = design_settings$place_x_axis_above,
            rotate_y_text = design_settings$rotate_y_text,
            diag_percentages_only = design_settings$diag_percentages_only,
            digits = as.integer(design_settings$num_digits),
            palette = palette,
            sums_settings = sums_settings,
            font_counts = do.call("font", counts_font_args),
            font_normalized = do.call("font", normalized_font_args),
            font_row_percentages = do.call("font", percentages_font_args),
            font_col_percentages = do.call("font", percentages_font_args),
            tile_border_color = tile_border_color,
            tile_border_size = design_settings$tile_border_size,
            tile_border_linetype = design_settings$tile_border_linetype
        )
    },
    error = function(e) {
        print("Failed to create plot from confusion matrix.")
        print(confusion_matrix)
        print(e)
        stop(e)
    }
)

# Add labels on x and y axes
confusion_matrix_plot <- confusion_matrix_plot +
    ggplot2::labs(
        x = design_settings$x_label,
        y = design_settings$y_label
    )

# Add title
if (nchar(design_settings$title_label) > 0) {
    confusion_matrix_plot <- confusion_matrix_plot +
        ggplot2::labs(
            title = design_settings$title_label
        )
}

# Add caption
if (nchar(design_settings$caption_label) > 0) {
    confusion_matrix_plot <- confusion_matrix_plot +
        ggplot2::labs(
            caption = design_settings$caption_label
        )
}


tryCatch(
    {
        ggplot2::ggsave(
            opt$out_path,
            width = design_settings$width,
            height = design_settings$height,
            dpi = design_settings$dpi,
            units = "px"
        )
    },
    error = function(e) {
        print(paste0("png: Failed to ggsave plot to: ", opt$out_path))
        print(e)
        stop(e)
    }
)

# Create a jpg version as well
tryCatch(
    {
        ggplot2::ggsave(
            paste0(substr(
                opt$out_path,
                start = 1,
                stop = nchar(opt$out_path) - 3
            ), "jpg"),
            width = design_settings$width,
            height = design_settings$height,
            dpi = design_settings$dpi,
            units = "px",
            bg = "white"
        )
    },
    error = function(e) {
        print(paste0("jpg: Failed to ggsave plot to: ", opt$out_path))
        print(e)
        stop(e)
    }
)
