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
- Add full reset button (empty cache on different files) - callback?
- Add option to change zero-tile background (e.g. to black for black backgrounds)
- Add option to format total-count tile in sum tiles
- Selectable templates (for 2,3,4,5 classes - one selects num classes and pick a color scheme and other common defaults)
- Add extra column in `Upload counts` that replaces whichever value is the bottom value (normally counts). Requires changes to cvms.
- Allow handling tick text - e.g. for long class names or many classes.
- Enable class order reversal after cvms arrow bug is fixed