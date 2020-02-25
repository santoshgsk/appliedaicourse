# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM jupyter/base-notebook

# If you prefer miniconda:
#FROM continuumio/miniconda3

USER root

RUN apt-get update && \
      apt-get -y install sudo

RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

RUN adduser jovyan sudo
RUN echo '\njovyan ALL=(ALL) NOPASSWD:ALL\n' >> /etc/sudoers

# LABEL Name=appliedaicourse Version=0.0.1
# EXPOSE 8080

WORKDIR /app
ADD . /app

RUN apt-get install -y curl gnupg2 
RUN curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
        apt-get update

USER jovyan
RUN sudo ACCEPT_EULA=y apt-get install -y msodbcsql17

        # optional: for bcp and sqlcmd
# RUN ACCEPT_EULA=Y apt-get install -y mssql-tools && \
#         echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile && \
#         echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc && \
#         source ~/.bashrc
        # # optional: for unixODBC development headers
        # apt-get instll unixodbc-dev


# Using pip:
RUN conda install -y --file requirements.txt
RUN conda install pytorch torchvision cpuonly -c pytorch
# CMD ["python3", "-m", "appliedaicourse"]

# Using pipenv:
#RUN python3 -m pip install pipenv
#RUN pipenv install --ignore-pipfile
#CMD ["pipenv", "run", "python3", "-m", "appliedaicourse"]

# Using miniconda (make sure to replace 'myenv' w/ your environment name):
#RUN conda env create -f environment.yml
#CMD /bin/bash -c "source activate myenv && python3 -m appliedaicourse"
