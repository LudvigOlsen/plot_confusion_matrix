# cvms_plot_app

Streamlit application for plotting a confusion matrix.


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
