FROM continuumio/miniconda3

WORKDIR /code

# Create the environment:
COPY ./environment.yml /code/environment.yml

RUN conda config --set channel_priority strict
RUN conda config --add channels conda-forge
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "plt_env", "/bin/bash", "-c"]

RUN pip install streamlit==1.23 Pillow lazyeval pandas streamlit-toggle-switch

# Demonstrate the environment is activated:
RUN echo "Make sure streamlit is installed:"
RUN python -c "import streamlit; print('streamlit: ', streamlit.__version__)"

COPY . .

# The code to run when container is started:

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "plt_env", "streamlit", "run", "app.py", "--server.port", "7860", "--server.address", "0.0.0.0"] 

