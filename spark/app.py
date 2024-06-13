from __future__ import print_function
from elasticsearch import Elasticsearch
from datetime import datetime,timedelta
import sys
import json
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.sql.dataframe import DataFrame
import time
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import RandomForestRegressor,LinearRegression,GBTRegressor
from pyspark.sql.types import IntegerType,DoubleType
from pyspark.sql.functions import array_contains
from pyspark.sql.functions import col
import os
import csv
from ultralytics import YOLO
import cv2
import math
import numpy as np
import base64
from io import BytesIO
from PIL import Image
sc = SparkContext(appName="PythonStructuredStreamsKafka")
spark = SparkSession(sc)
print(spark.version)
sc.setLogLevel("WARN")

kafkaServer="kafka:39092"
topic = "safeGuard"

def check_elasticsearch_connection():
    es = Elasticsearch("http://elasticsearch:9200")
    return es.ping()


# Funzione per inviare i dati a Elasticsearch
def send_to_elasticsearch(batch_df: DataFrame, batch_id: int):
    es = Elasticsearch("http://elasticsearch:9200")  
    if not es.ping():
        raise ValueError("Impossibile connettersi a Elasticsearch")

    records = batch_df.toJSON().map(json.loads).collect()
    data_corrente = datetime.now()
    data_formattata = data_corrente.strftime("%d/%m/%Y")
    classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]
    for record in records:
        converted_dict = json.loads(record["value"])

    # Invio dei dati a Elasticsearch
    for record in records:
        objectsfounds = {key: 0 for key in classNames}
        converted_dict = json.loads(record["value"])
        doc_id =  int(str(time.time()).replace(".", ""))   
        model = YOLO("yolo-Weights/yolov8n.pt")
        image_data = base64.b64decode(converted_dict["image"])
        image_buffer = BytesIO(image_data)
        img_cv2 = Image.open(image_buffer)
        results = model(img_cv2)
        # Coordinati
        for r in results:
            boxes = r.boxes
        # Converti l'immagine PIL in un array NumPy
        img_cv2 = np.array(img_cv2)
        
        for box in boxes:
            # Rettangolo delimitatore
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)  # converte in valori int

            # Disegna il rettangolo sull'immagine
            cv2.rectangle(img_cv2, (x1, y1), (x2, y2), (255, 0, 255), 2)

            # Confidence
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            cv2.putText(img_cv2, classNames[cls], org, font, fontScale, color, thickness)
            objectsfounds[classNames[cls]] += 1
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        _, buffer = cv2.imencode('.png', img_cv2)
        encoded_img = base64.b64encode(buffer).decode('utf-8')
        converted_dict["image2"]=encoded_img
        converted_dict["url"]="http://165.232.116.229:9393/getimage/"+str(doc_id)
        converted_dict["data"]=data_formattata
        converted_dict["objectsfount"]=objectsfounds
        update_body = {
            "doc": converted_dict,
            "doc_as_upsert": True
        }

        es.update(index="movements", id=doc_id, body=update_body)

# Streaming Query


while not check_elasticsearch_connection():
    print("Connessione a ElasticSearch in corso...")
    time.sleep(3)  # Attendi 3 secondi prima di verificare nuovamente la connessione

print("Connessione a ElasticSearch stabilita.")


df = spark \
  .readStream \
  .format("kafka") \
  .option("kafka.bootstrap.servers", kafkaServer) \
  .option("subscribe", topic) \
  .load()

df.selectExpr("CAST(timestamp AS STRING)","CAST(value AS STRING)") \
  .writeStream \
  .foreachBatch(send_to_elasticsearch) \
  .start() \
  .awaitTermination()
