FROM continuumio/miniconda3

WORKDIR /code

# Create the environment:
COPY ./environment.yml /code/environment.yml
RUN conda create -f environment.yml -y

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "plt_env", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
RUN echo "Make sure utipy is installed:"
RUN python -c "import utipy"

COPY . .

# The code to run when container is started:
# server.address 0.0.0.0 ?

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "plt_env", "streamlit", "run", "app.py", "--server.port", "7860"] 

