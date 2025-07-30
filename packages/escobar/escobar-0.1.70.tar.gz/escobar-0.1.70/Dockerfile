FROM python:3.10-slim

# Install dependencies for building and curl/gpg
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    git \
    make \
    gcc \
    g++ \
    xz-utils \
    jupyter-core \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v24 manually
ENV NODE_VERSION=24.0.0



# Set working directory
WORKDIR /app

# COPY . .

RUN pip3 install escobar==0.1.41 aiohttp jupyter jupyterlab voitta

EXPOSE 8888

# Set environment variables from .env file at runtime
ENV DEBUG=1
ENV DEMO_USERS=roman,gregory,yc
ENV SERVER_URL=ws://44.226.253.156:8777/ws

# Start JupyterLab
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--no-browser", "--NotebookApp.token=''", "--NotebookApp.password=''"]]
