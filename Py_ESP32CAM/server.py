import cv2
from urllib.request import urlopen
import numpy as np

# Cargar el modelo preentrenado para la detección de objetos
net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'deploy.caffemodel')

# Lista de clases del modelo entrenado
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Conexión con la cámara ESP32
stream = urlopen('http://192.168.0.154/stream')
bytes = bytes()

while True:
    bytes += stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a != -1 and b != -1:
        jpg = bytes[a:b+2]
        bytes = bytes[b+2:]
        if jpg:
            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Detección de persona
            h, w = img.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 0.007843, (300, 300), 127.5)
            net.setInput(blob)
            detections = net.forward()

            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:  # Umbral de confianza
                    idx = int(detections[0, 0, i, 1])
                    if CLASSES[idx] == "person":  # Solo interesan las detecciones de personas
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")
                        cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)
                        
                        # Calcular el centro de la caja delimitadora
                        centerX = (startX + endX) // 2
                        centerY = (startY + endY) // 2
                        
                        # Control del auto basado en la posición de la persona
                        if centerX < w // 3:
                            print("Girar a la izquierda")
                            # Código para girar el auto a la izquierda
                        elif centerX > 2 * w // 3:
                            print("Girar a la derecha")
                            # Código para girar el auto a la derecha
                        else:
                            print("Adelante")
                            # Código para avanzar el auto
                        
            cv2.imshow('ESP32 CAM', img)

    if cv2.waitKey(1) & 0xff == ord('q'):
        break

stream.close()
cv2.destroyAllWindows()
