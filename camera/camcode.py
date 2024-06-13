import cv2
import numpy as np
import time
from pathlib import Path
import requests
from PIL import Image
import io
import hashlib
import json
import base64
def detect_motion():
   # url = inserire url e porta fluent
    # Attiva la webcam
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    i = 0

    # Inizializza il primo frame per il confronto
    first_frame = None

    # Inizializza il timestamp per la gestione del delay
    last_detection_time = 0
    detection_delay = 5  # delay in seconds

    while True:
        # Legge il frame corrente dalla webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Converte il frame in scala di grigi
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Se il primo frame è None, inizializzalo
        if first_frame is None:
            first_frame = gray
            continue

        # Calcola la differenza tra il primo frame e il frame corrente
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

        # Dilata l'immagine threshold per riempire i buchi, poi trova i contorni
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Flag per rilevare se un movimento è stato trovato
        motion_detected = False

        # Loop sui contorni trovati
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue

            # Se viene rilevato un movimento, stampa "DETECTION RILEVATA"
            current_time = time.time()
            if current_time - last_detection_time > detection_delay:
                frame_filename = f"detected_frame_{i}.PNG"
                #image = Image.fromarray(frame)
                image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                # Crea un buffer di byte in memoria
                buffer = io.BytesIO()

                # Salva l'immagine nel buffer come PNG
                image.save(buffer, format='PNG')

                # Ottieni i byte dal buffer
                image_bytes = buffer.getvalue()
                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                #cv2.imwrite(frame_filename, frame)
                data=({"image":image_base64,"imgname":frame_filename,"idcamera":"camera1"})
                print(image_base64[0:1])
                headers = {'Content-Type': 'application/json'}
                # with open('image_base64.txt', 'w') as file:
                #     file.write(image_base64)
                response = requests.post(url, json=data,headers=headers)
                print(response.status_code)
                
                i += 1
                last_detection_time = current_time
                motion_detected = True
                break

        # Se il movimento è stato rilevato, aggiorna il first_frame
        if motion_detected:
            first_frame = gray

        # Mostra il flusso video originale della webcam
        #cv2.imshow("Webcam Feed", frame)

        # Interrompi il ciclo premendo 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Rilascia la webcam e chiudi tutte le finestre
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_motion()
