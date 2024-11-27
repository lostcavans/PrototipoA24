import requests  # Importa la librería requests para enviar el texto al ESP8266
from tkinter import *
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import numpy as np

def onClossing():
    root.quit()
    cap.release()
    root.destroy()

def enviar_comando_esp8266(mensaje):
    esp8266_ip = 'http://192.168.1.100'  # Reemplaza con la IP del ESP8266
    try:
        # Enviar el mensaje (posición) al ESP8266 a través de una solicitud HTTP
        response = requests.get(f"{esp8266_ip}/mensaje?text={mensaje}")
        if response.status_code == 200:
            print(f"Mensaje enviado al ESP8266: {mensaje}")
        else:
            print(f"Error al enviar el mensaje: {response.status_code}")
    except Exception as e:
        print(f"Error al conectar con el ESP8266: {e}")

def callback():
    cap.open(url)  # Abrimos la url antes de capturar el frame

    ret, frame = cap.read()
    
    if ret:
        height, width, _ = frame.shape  # Obtener dimensiones del frame

        # Predicción con el modelo YOLO
        results = model.predict(frame, stream=True, verbose=False)
        
        for result in results:
            boxes = result.boxes
            annotator = Annotator(frame)

            for box in boxes:
                r = box.xyxy[0]  # Coordenadas del cuadro [x1, y1, x2, y2]
                x_center = (r[0] + r[2]) / 2  # Centro del cuadro delimitador
                c = box.cls

                if classes[int(c)] == "persona":
                    # Determinar la posición de la persona respecto al ancho de la imagen
                    if x_center < width / 3:
                        position = "izquierda"
                        mensaje = "¡Persona detectada a la izquierda!"
                    elif x_center > 2 * width / 3:
                        position = "derecha"
                        mensaje = "¡Persona detectada a la derecha!"
                    else:
                        position = "centro"
                        mensaje = "¡Persona detectada a la centro!"

                    print(mensaje)
                    enviar_comando_esp8266(mensaje)  # Enviar el mensaje al ESP8266
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
url = 'http://192.168.1.102/480x320.jpg'
cap = cv2.VideoCapture(url)  # Crear objeto VideoCapture

if cap.isOpened():
    print("Cámara iniciada")
else:
    sys.exit("Cámara desconectada")

############################## HMI design #################
root = Tk()
root.protocol("WM_DELETE_WINDOW", onClossing)
root.title("Vision Artificial")  # Título de la ventana

label = Label(root)  # Label donde se mostrará la imagen
label.grid(row=1, padx=20, pady=20)

root.after(1, callback)  # Comenzar el ciclo de captura
root.mainloop()
