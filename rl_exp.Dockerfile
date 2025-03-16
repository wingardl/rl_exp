FROM pytorch/pytorch:2.6.0-cuda12.6-cudnn9-devel

WORKDIR /app

# Install system dependencies for CodeQL
RUN apt-get update && apt-get install -y \
    git \
    wget \
    unzip \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*


    # Download the CodeQL bundle (CLI + compatible query packs)
RUN wget https://github.com/github/codeql-action/releases/download/codeql-bundle-v2.20.6/codeql-bundle-linux64.tar.gz -O /tmp/codeql-bundle.tar.gz \
&& mkdir -p /opt/codeql-bundle \
&& tar -xzf /tmp/codeql-bundle.tar.gz -C /opt/codeql-bundle --strip-components=1 \
&& rm /tmp/codeql-bundle.tar.gz \
&& ln -s /opt/codeql-bundle/codeql/codeql /usr/local/bin/codeql



# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Copy project files (before running uv sync)
COPY . .

# Now run uv sync with project files available
RUN uv sync

# Set PATH to include CodeQL
ENV PATH="/opt/codeql-bundle:${PATH}"

RUN chmod +x /opt/codeql-bundle/codeql

# Set the default command
# CMD ["python", "rl_grpo.py"]