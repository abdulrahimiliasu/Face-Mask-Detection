from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tkinter import messagebox
import numpy as np
import cv2
from interface import Interface


class ImageMaskDetection:

    def __init__(self, image_path):
        self.CONFIDENCE = 0.5
        ImageMaskDetection.update_progress_bar(10)
        prototxt_path = 'caffe_dnn/deploy.prototxt'
        caffemodel_path = 'caffe_dnn/res10_300x300_ssd_iter_140000.caffemodel'
        network = cv2.dnn.readNet(prototxt_path, caffemodel_path)
        ImageMaskDetection.update_progress_bar(30)
        self.model = load_model('mask_model')
        try:
            self.image = cv2.imread(image_path)
            if self.image is None:
                raise AttributeError
        except AttributeError:
            messagebox.showerror(title="Error Loading Image", message=f"The Image could not be loaded, Please check "
                                                                      f"the path and try again {image_path}!")
        else:
            (self.height, self.width) = self.image.shape[:2]
            ImageMaskDetection.update_progress_bar(60)
            blob = cv2.dnn.blobFromImage(self.image, 1.0, (300, 300), (104.0, 177.0, 123.0))
            network.setInput(blob)
            self.detections = network.forward()
            ImageMaskDetection.update_progress_bar(80)

    @staticmethod
    def update_progress_bar(value):
        Interface.progress_bar['value'] = value
        Interface.window.update_idletasks()

    @staticmethod
    def update_info_text(text):
        Interface.info_text.config(text=text)
        Interface.window.update_idletasks()
        Interface.window.update()

    def start_mask_detections(self):
        num_of_faces = 0
        ImageMaskDetection.update_progress_bar(100)
        ImageMaskDetection.update_info_text("press 'q' to quit window")
        for i in range(0, self.detections.shape[2]):
            confidence = self.detections[0, 0, i, 2]
            if confidence > self.CONFIDENCE:
                num_of_faces += 1
                print(f"\nDETECTED FACES: {num_of_faces}")
                box = self.detections[0, 0, i, 3:7] * np.array([self.width, self.height, self.width, self.height])
                (startX, startY, endX, endY) = box.astype("int")
                # ensure the bounding boxes fall within the dimensions of the frame
                (startX, startY) = (max(0, startX), max(0, startY))
                (endX, endY) = (min(self.width - 1, endX), min(self.height - 1, endY))
                # extract the face ROI, convert it from BGR to RGB channel ordering, resize it to 224x224, and preprocess it
                face = self.image[startY:endY, startX:endX]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)
                face = np.expand_dims(face, axis=0)

                (mask, withoutMask) = self.model.predict(face)[0]

                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                cv2.putText(self.image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(self.image, (startX, startY), (endX, endY), color, 2)
                print(f"position: top_left{startX, startY} bottom_right{endX, endY}")
            ImageMaskDetection.update_info_text(f"Detected {num_of_faces} Faces")
            cv2.imshow("press 'q' to quit window", self.image)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                ImageMaskDetection.update_progress_bar(0)
                ImageMaskDetection.update_info_text("")
                break
