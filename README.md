---
title: plot_confusion_matrix
sdk: streamlit
python_version: 3.11
sdk_version: 1.19.0
app_file: app.py
pinned: true
---

# cvms_plot_app

Streamlit application for plotting a confusion matrix.

emoji: {{emoji}}
colorFrom: {{colorFrom}}
colorTo: {{colorTo}}


## TODOs

- IMPORTANT! Allow specifying which class probabilities are of! (See plot prob_of_class)
- Allow setting threshold - manual, max J, spec/sens
- Add bg box around confusion matrix plot as text dissappears on dark mode!
- ggsave does not use dpi??
- Allow svg, pdf?
- Add full reset button (empty cache on different files) - callback?
- Handle <2 classes in design box (add st.error)
- Handle classes with spaces in them?
- Add option to change zero-tile background (e.g. to black for black backgrounds)
- Add option to format total-count tile in sum tiles
