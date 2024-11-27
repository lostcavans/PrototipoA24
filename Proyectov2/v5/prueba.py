import requests
from tkinter import *
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import numpy as np
import time

def onClossing():
    """
    Finaliza el programa y libera recursos.
    """
    root.quit()
    cap.release()
    root.destroy()

def enviar_comando_esp8266(mensaje):
    """
    Envía comandos al ESP8266 para controlar el auto.
    """
    esp8266_ip = 'http://192.168.1.102'
    try:
        response = requests.get(f"{esp8266_ip}/mensaje?text={mensaje}", timeout=2)
        if response.status_code == 200:
            print(f"Mensaje enviado al ESP8266: {mensaje}")
        else:
            print(f"Error al enviar el mensaje: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar con el ESP8266: {e}")

def evitar_obstaculo():
    """
    Rutina para evitar obstáculos.
    """
    print("Evitando obstáculo...")
    enviar_comando_esp8266("girar_derecha")  # Gira a la derecha
    time.sleep(1)  # Tiempo para rodear el obstáculo
    enviar_comando_esp8266("avanzar")  # Avanza
    time.sleep(2)
    enviar_comando_esp8266("girar_izquierda")  # Regresa a la trayectoria
    time.sleep(1)

def detectar_color(frame, box):
    """
    Detecta si la persona tiene polera azul dentro del cuadro delimitador.
    """
    x1, y1, x2, y2 = map(int, box)
    cropped = frame[y1:y2, x1:x2]
    hsv_cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)
    
    # Rango de color azul en HSV
    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([140, 255, 255])
    
    mask = cv2.inRange(hsv_cropped, lower_blue, upper_blue)
    blue_ratio = cv2.countNonZero(mask) / (cropped.shape[0] * cropped.shape[1])
    
    return blue_ratio > 0.2  # Devuelve True si más del 20% del área es azul

def obtener_distancia_obstaculo():
    """
    Obtiene la distancia al obstáculo desde un sensor ultrasonido.
    (Simulado, reemplazar con hardware real).
    """
    return 50  # Simula una distancia de 50 cm; reemplaza con datos reales del sensor

def callback():
    """
    Procesa cada cuadro de la cámara, detecta personas y obstáculos.
    """
    global last_message, last_send_time
    cap.open(url)

    ret, frame = cap.read()
    
    if ret:
        height, width, _ = frame.shape
        results = model.predict(frame, stream=True, verbose=False)
        
        persona_detectada = False

        for result in results:
            boxes = result.boxes
            annotator = Annotator(frame)

            for box in boxes:
                r = box.xyxy[0]
                x_center = (r[0] + r[2]) / 2
                c = box.cls
                box_area = (r[2] - r[0]) * (r[3] - r[1])
                frame_area = height * width

                if classes[int(c)] == "persona" and detectar_color(frame, r):
                    persona_detectada = True
                    if box_area > 0.6 * frame_area:
                        mensaje = "muy_cerca"
                    else:
                        if x_center < width / 3:
                            mensaje = "izquierda"
                        elif x_center > 2 * width / 3:
                            mensaje = "derecha"
                        else:
                            mensaje = "centro"

                    # Enviar comandos para seguir a la persona
                    current_time = time.time()
                    if mensaje != last_message or (current_time - last_send_time > SEND_INTERVAL):
                        print(f"Mensaje: {mensaje}")
                        enviar_comando_esp8266(mensaje)
                        last_message = mensaje
                        last_send_time = current_time

                    annotator.box_label(r, label=f"{classes[int(c)]}", color=(0, 0, 255))  # Rojo para destacar

        if not persona_detectada:
            # Si no se detecta persona, verifica obstáculos
            distancia = obtener_distancia_obstaculo()
            if distancia < 30:  # Obstáculo cercano (umbral en cm)
                evitar_obstaculo()
            else:
                enviar_comando_esp8266("detener")

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        tkimage = ImageTk.PhotoImage(img)
        label.configure(image=tkimage)
        label.image = tkimage

        root.after(1, callback)

    else:
        onClossing()

# Configuración del modelo YOLO
model = YOLO("yolov8n.pt")

# Cargar nombres de las clases desde el archivo coco.names
classesFile = "coco.names"
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# URL de la cámara
url = 'http://192.168.1.100/480x320.jpg'
cap = cv2.VideoCapture(url)

if cap.isOpened():
    print("Cámara iniciada")
else:
    sys.exit("Cámara desconectada")

# Configuración de la interfaz
root = Tk()
root.protocol("WM_DELETE_WINDOW", onClossing)
root.title("Visión Artificial")

label = Label(root)
label.grid(row=1, padx=20, pady=20)

# Variables globales
last_message = None
last_send_time = 0
SEND_INTERVAL = 2  # Intervalo mínimo entre mensajes al ESP8266

root.after(1, callback)
root.mainloop()
