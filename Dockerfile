ARG python=python:3.9.13-slim-bullseye

FROM ${python}

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>


# add and install python requirements
RUN pip install --upgrade pip --no-cache-dir
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir


# # setup user and group ids
ARG USER_ID=1001
ENV USER_ID $USER_ID
ARG GROUP_ID=1001
ENV GROUP_ID $GROUP_ID

# # add non-root user and give permissions to workdir
RUN groupadd --gid $GROUP_ID appuser && \
          adduser appuser --ingroup appuser --gecos '' --disabled-password --uid $USER_ID && \
          mkdir -p /usr/src/app && \
          chown -R appuser:appuser /usr/src/app


# #switch user
USER appuser

# Copy app files to container
WORKDIR /usr/src/app
COPY ./app .

RUN python ./__init__.py

CMD streamlit run --server.port 80 main.py