---
title: Plot Confusion Matrix
sdk: docker
app_file: app.py
pinned: true
emoji: 🍀
colorFrom: orange
colorTo: purple
---

# Plot Confusion Matrix Streamlit Application

Streamlit application for plotting a confusion matrix.


## TODOs
- ggsave only uses DPI for scaling? We would expect output files to have the given DPI?
- Allow svg, pdf?
- Add option to change zero-tile background (e.g. to black for black backgrounds)
- Add option to format total-count tile in sum tiles
- Allow handling tick text - e.g. for long class names or many classes.