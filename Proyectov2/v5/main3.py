import requests
from tkinter import *
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import numpy as np
import time

def onClossing():
    root.quit()
    cap.release()
    root.destroy()

def enviar_comando_esp8266(mensaje):
    esp8266_ip = 'http://192.168.1.103'
    try:
        response = requests.get(f"{esp8266_ip}/mensaje?text={mensaje}", timeout=5)
        if response.status_code == 200:
            print(f"Mensaje enviado al ESP8266: {mensaje}")
        else:
            print(f"Error al enviar el mensaje: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar con el ESP8266: {e}")

last_message = None
last_send_time = 0
SEND_INTERVAL = 2

def callback():
    global last_message, last_send_time
    cap.open(url)

    ret, frame = cap.read()
    
    if ret:
        height, width, _ = frame.shape
        results = model.predict(frame, stream=True, verbose=False)
        
        for result in results:
            boxes = result.boxes
            annotator = Annotator(frame)

            for box in boxes:
                r = box.xyxy[0]
                x_center = (r[0] + r[2]) / 2
                c = box.cls
                box_area = (r[2] - r[0]) * (r[3] - r[1])
                frame_area = height * width

                position = "desconocida"  # Valor por defecto para evitar errores
                if classes[int(c)] == "persona":
                    if box_area > 0.6 * frame_area:
                        mensaje = "¡Persona muy cerca de la cámara!"
                    else:
                        if x_center < width / 3:
                            position = "izquierda"
                            mensaje = "¡Persona detectada a la izquierda!"
                        elif x_center > 2 * width / 3:
                            position = "derecha"
                            mensaje = "¡Persona detectada a la derecha!"
                        else:
                            position = "centro"
                            mensaje = "¡Persona detectada al centro!"

                    # Enviar solo si el mensaje cambió o pasó el intervalo
                    current_time = time.time()
                    if mensaje != last_message or (current_time - last_send_time > SEND_INTERVAL):
                        print(mensaje)
                        enviar_comando_esp8266(mensaje)
                        last_message = mensaje
                        last_send_time = current_time

                    annotator.box_label(r, label=f"{classes[int(c)]} ({position})", color=tuple(COLORS[int(c)]))
                
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        tkimage = ImageTk.PhotoImage(img)
        label.configure(image=tkimage)
        label.image = tkimage

        root.after(1, callback)

    else:
        onClossing()

# Cargar el modelo YOLO
model = YOLO("yolov8n.pt")

# Cargar nombres de las clases desde el archivo coco.names
classesFile = "coco.names"
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
    COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

# URL de la cámara
url = 'http://192.168.1.102/800x600.jpg'
cap = cv2.VideoCapture(url)

if cap.isOpened():
    print("Cámara iniciada")
else:
    sys.exit("Cámara desconectada")

# Configuración de la interfaz
root = Tk()
root.protocol("WM_DELETE_WINDOW", onClossing)
root.title("Vision Artificial")

label = Label(root)
label.grid(row=1, padx=20, pady=20)

root.after(1, callback)
root.mainloop()
