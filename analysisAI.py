import torch
import cv2
import numpy as np
from PIL import Image
import base64
from helpers import apology

#model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)  # Use YOLOv5s, "s" small but fastermodel
model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)  # Use YOLOv5x, "x" large but slower model

def detect_objects(img_path):

    img = Image.open(img_path)
    results = model(img)

    # Convertir la imagen a un formato que OpenCV pueda usar
    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    detected_objects = results.pandas().xyxy[0]
    print("detected_objects: ", detected_objects)

    filtered_objects = detected_objects[~detected_objects['name'].isin(["person", "wall", "brick", "road", "animal", "dog", "cat", "window", "baby", "teeth"])]

    if filtered_objects.empty:
        print("No objects detected")
        return apology("No objects detected", 500)
    
    else:
        for index, row in filtered_objects.iterrows():
            if row['name'] not in ["person", "wall", "brick", "road", "animal", "dog", "cat", "window", "baby"]:
                color = (0, 255, 0)  # Color para los recuadros
                label = f"{row['name']} {row['confidence']:.2f}"
                cv2.rectangle(cv_img, 
                (int(row['xmin']), int(row['ymin'])), 
                (int(row['xmax']), int(row['ymax'])), 
                color, 2)
                cv2.putText(cv_img, label, (int(row['xmin']), int(row['ymin']-10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        processed_img_path = "processed_temp.jpg"
        cv2.imwrite(processed_img_path, cv_img)

    print("filtered_objects: ", filtered_objects)
    return filtered_objects, processed_img_path
