FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel

WORKDIR /app

# Install system dependencies for CodeQL
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install CodeQL CLI
RUN wget https://github.com/github/codeql-cli-binaries/releases/download/v2.15.5/codeql-linux64.zip -O /tmp/codeql.zip \
    && unzip /tmp/codeql.zip -d /opt \
    && rm /tmp/codeql.zip \
    && ln -s /opt/codeql/codeql /usr/local/bin/codeql
# install curl
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# set home path
RUN source $HOME/.local/bin/env 

RUN uv sync
# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app


# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Copy project files
COPY . .

RUN uv sync

# Set PATH to include CodeQL
ENV PATH="/opt/codeql:${PATH}"

# Set the default command
# CMD ["python", "rl_grpo.py"]