FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RESULTS_ROOT=/data/results \
    KPML_HOME=/opt/kpml

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       git \
       sbcl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY . /workspace

RUN chmod +x /workspace/bootstrap/build_remote_runtime.sh \
    && mkdir -p /data/results /opt/kpml

EXPOSE 7860

CMD ["uvicorn", "hf-space.app:app", "--host", "0.0.0.0", "--port", "7860"]
