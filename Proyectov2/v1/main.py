import cv2
import numpy as np

# Cargar YOLO (reemplaza con las rutas a los archivos descargados)
yolo_net = cv2.dnn.readNet("Object-Detection---Yolov3-master/model/yolov3.weights", "darknet-master/cfg/yolov3.cfg")
layer_names = yolo_net.getLayerNames()
output_layers = [layer_names[i[0] - 1] for i in yolo_net.getUnconnectedOutLayers()]

# Cargar las clases de objetos
with open("yolo/coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Cargar una imagen para hacer la detección
img = cv2.imread("test.jpg")
height, width, channels = img.shape

# Preprocesar la imagen para YOLO
blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
yolo_net.setInput(blob)
outs = yolo_net.forward(output_layers)

# Mostrar información en pantalla y dibujar los rectángulos
class_ids = []
confidences = []
boxes = []

for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:  # Umbral de confianza
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)

            # Coordenadas del rectángulo
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)

            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

# Aplicar supresión de no máximos para eliminar múltiples cajas detectadas del mismo objeto
indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

# Dibujar las cajas y los nombres de los objetos detectados
font = cv2.FONT_HERSHEY_PLAIN
for i in range(len(boxes)):
    if i in indexes:
        x, y, w, h = boxes[i]
        label = str(classes[class_ids[i]])
        color = (0, 255, 0)  # Color verde para la caja
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, label, (x, y + 30), font, 2, color, 2)

# Mostrar la imagen con las detecciones
cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
