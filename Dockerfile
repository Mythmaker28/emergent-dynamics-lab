# Isolated, pinned environment for `make reproduce-paper`.
FROM python:3.11-slim
RUN pip install --no-cache-dir "numpy==2.1.3" "sympy==1.13.3"
WORKDIR /repo
COPY . /repo
ENV PYTHONHASHSEED=0 PYTHONPYCACHEPREFIX=/tmp/rpc
CMD ["make", "reproduce-paper"]
