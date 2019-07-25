FROM python:3.6-stretch
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade colorlog black pylint pytest aiohttp pytest-asyncio twine
WORKDIR /workspace

# Set the default shell to bash instead of sh
ENV SHELL /bin/bash