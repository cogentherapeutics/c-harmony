# We use the build environment to create the correct python version with pyenv
# and the correct virtual environment with pipenv.
FROM public.ecr.aws/lts/ubuntu:22.04_stable AS builder

LABEL maintainer="CHANGEME <changeme@repertoire.com>"

ENV PIPENV_VENV_IN_PROJECT=1
ENV PYENV_GIT_TAG=v2.3.32
# TODO: Using the root user and directory as $HOME goes against good practices
# and security concerns. To be replaced in the future...
ENV PYENV_ROOT=/root/.pyenv
ENV PATH=/root/.pyenv/bin:$PATH

ADD Pipfile.lock Pipfile /root/

WORKDIR /root

RUN apt-get update \
    && apt-get install -y \
        build-essential=12.9ubuntu3 \
        curl=7.81.0-1ubuntu1.15 \
        git=1:2.34.1-1ubuntu1.10 \
        libbz2-dev=1.0.8-5build1 \
        libffi-dev=3.4.2-4 \
        libreadline-dev=8.1.2-1 \
        libsqlite3-dev=3.37.2-2ubuntu0.3 \
        libssl-dev=3.0.2-0ubuntu1.12 \
        zlib1g-dev=1:1.2.11.dfsg-2ubuntu9.2 \
    && curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer \
    | bash \
    && /root/.pyenv/bin/pyenv install 3.10.13 \
    && eval "$(/root/.pyenv/bin/pyenv init --path)" \
    && /root/.pyenv/bin/pyenv local 3.10.13 \
    && pip install "pipenv>=2023.11.15" \
    && pipenv sync

# We copy over from the build environment the compiled python and virtual
# environments to minimize the container size and prepare integrating
# the application source.
FROM public.ecr.aws/lts/ubuntu:22.04_stable AS application

LABEL maintainer="CHANGEME <changeme@repertoire.com>"

COPY --from=builder /root/.pyenv /root/.pyenv
COPY --from=builder /root/.venv /root/.venv

# TODO: Using the root user and directory as $HOME goes against good practices
# and security concerns. To be replaced in the future...
RUN apt-get update \
    && echo 'eval "$(/root/.pyenv/bin/pyenv init --path)"' >> /root/.bashrc

ENV PYENV_ROOT=/root/.pyenv
ENV PATH=/root/.venv/bin:/root/.pyenv/bin:$PATH

COPY VERSION /root/VERSION
COPY src /root/src

WORKDIR /root

CMD sleep infinity

