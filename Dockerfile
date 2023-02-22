FROM python:3.6
MAINTAINER Marcos Federico Mandrille <mmandrille@gmail.com>

# Base installs
RUN apt-get update
RUN apt-get install -y libopenblas-dev gfortran

# Virtual Enviroment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Requierements installation
RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install cython
RUN pip install numpy==1.12.1
RUN pip install scipy==0.19.0
RUN pip install gunicorn==19.7.1
RUN pip install flask==0.12.2
RUN pip install image-match==1.1.2
RUN pip install "elasticsearch>=6.0.0,<7.0.0"
RUN rm -rf /var/lib/apt/lists/*

# Generate Matlib Cache
RUN python -c "import matplotlib as mpl"

# Enviroment Variables, you can overwrite them
ENV PORT=80
ENV WORKER_COUNT=4
ENV TIMEOUT=60
ENV ELASTICSEARCH_URL=localhost:9200
ENV ELASTICSEARCH_INDEX=images
ENV ELASTICSEARCH_DOC_TYPE=images
ENV ALL_ORIENTATIONS=true

# Copy files
COPY entrypoint.sh /
RUN chmod +x entrypoint.sh
COPY wait-for-it.sh /
RUN chmod +x wait-for-it.sh
COPY server.py /
RUN chmod +x server.py

# Run:
ENTRYPOINT ["/bin/bash", "-c", "/entrypoint.sh"]