


ARG IMAGE_VARIANT=slim-buster
ARG OPENJDK_VERSION=8
ARG PYTHON_VERSION=3.9.8

FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT} AS py3
FROM openjdk:${OPENJDK_VERSION}-${IMAGE_VARIANT}

COPY --from=py3 / /

ARG PYSPARK_VERSION=3.4.0
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
RUN pip --no-cache-dir install pyspark==${PYSPARK_VERSION}
RUN pip --no-cache-dir install elasticsearch
RUN pip --no-cache-dir install numpy
RUN pip --no-cache-dir install opencv-python
RUN pip --no-cache-dir install ultralytics


COPY app.py .
RUN mkdir dataset_output

CMD spark-submit --master local[1] --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0 app.py 
