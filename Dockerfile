# Isolated, pinned environment for `make reproduce-all`. python:3.11-slim lacks build tools -> install make.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir "numpy==2.1.3" "matplotlib==3.9.2" "sympy==1.13.3"
WORKDIR /repo
COPY . /repo
ENV PYTHONHASHSEED=0 PYTHONPYCACHEPREFIX=/tmp/rpc
CMD ["make", "reproduce-all"]
