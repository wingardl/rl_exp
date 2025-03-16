FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel

WORKDIR /app

# Install system dependencies for CodeQL
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install CodeQL repo
RUN wget https://github.com/github/codeql-cli-binaries/releases/download/v2.15.5/codeql-linux64.zip -O /tmp/codeql.zip \
    && unzip /tmp/codeql.zip -d /opt \
    && rm /tmp/codeql.zip \
    && ln -s /opt/codeql/codeql /usr/local/bin/codeql

# Download and extract CodeQL query packs to the same directory as the CLI
RUN codeql pack download --dir=/opt/codeql codeql/cpp-queries:codeql-cpp \
    codeql/java-queries:codeql-java \
    codeql/python-queries:codeql-python \
    codeql/javascript-queries:codeql-javascript \
    codeql/csharp-queries:codeql-csharp \
    codeql/go-queries:codeql-go \
    codeql/ruby-queries:codeql-ruby

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project files (before running uv sync)
COPY . .

# Now run uv sync with project files available
RUN uv sync

# Set PATH to include CodeQL
ENV PATH="/opt/codeql:${PATH}"

# Set the default command
# CMD ["python", "rl_grpo.py"]