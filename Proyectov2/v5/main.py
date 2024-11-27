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
                    elif x_center > 2 * width / 3:
                        position = "derecha"
                    else:
                        position = "centro"

                    print(f"¡Persona detectada a la {position}!")
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
url = 'http://192.168.1.101/480x320.jpg'
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
