FROM mcr.microsoft.com/vscode/devcontainers/anaconda:0-3



# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>


# add and install python requirements
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt


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
# COPY ./.streamlit ./.streamlit

# EXPOSE 80

# ENTRYPOINT ["streamlit", "run", "--server.port", "80"]

CMD streamlit run --server.port 80 main.py