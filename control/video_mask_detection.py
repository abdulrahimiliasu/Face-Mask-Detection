from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from view.interface import Interface
from tkinter import PhotoImage, messagebox
from notification import Notification
import pygame
import numpy as np
import imutils
import time
import cv2


last_read_frame = None
no_mask = None


class VideoMaskDetection:

    count = 0
    flag = False
    captured_img = PhotoImage(file='../captures/last_capture.png')

    def __init__(self):
        """
        Initializes a VideoMaskDetection Object with a default confidence of 0.5 and loads face
        detector model, mask model
        and alert sound from disk.
        """
        self.CONFIDENCE = 0.5
        Interface.update_progress_bar(20)
        self.prototxtPath = 'caffe_dnn/deploy.prototxt'
        Interface.update_progress_bar(30)
        self.caffePath = 'caffe_dnn/res10_300x300_ssd_iter_140000.caffemodel'
        self.faceModel = cv2.dnn.readNet(self.prototxtPath, self.caffePath)
        Interface.update_progress_bar(50)
        self.maskModel = load_model('mask_model')
        Interface.update_progress_bar(70)
        pygame.mixer.init()
        pygame.mixer.music.load("sounds/beep.mp3")

    def detect_and_predict(self, video_frame, face_model, mask_model):
        """
        Makes a face detection from frame and predict face mask detection if any face is found.
        :param video_frame: frame to make the detection on
        :param face_model: face detection model
        :param mask_model: mask detection model
        :return: list of locations and predictions of the faces found on the frame
        """
        (h, w) = video_frame.shape[:2]
        blob = cv2.dnn.blobFromImage(video_frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
        # pass the blob through the network and obtain the face detections
        face_model.setInput(blob)
        detections = face_model.forward()

        faces = []
        locations = []
        predictions = []

        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.CONFIDENCE:
                face_box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = face_box.astype("int")
                (start_x, start_y) = (max(0, start_x), max(0, start_y))
                (end_x, end_y) = (min(w - 1, end_x), min(h - 1, end_y))

                face = video_frame[start_y:end_y, start_x:end_x]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = cv2.resize(face, (224, 224))
                face = img_to_array(face)
                face = preprocess_input(face)

                faces.append(face)
                locations.append((start_x, start_y, end_x, end_y))

        if len(faces) > 0:
            # for faster inference we'll make batch predictions on *all* faces at the same time rather than one-by-one
            # predictions in the above `for` loop
            faces = np.array(faces, dtype="float32")
            predictions = mask_model.predict(faces, batch_size=32)
        elif VideoMaskDetection.flag:
            VideoMaskDetection.save_offender_image()
            if Interface.auto_send_is_on.get():
                Notification.notify(show_messagebox=False)

        return locations, predictions

    @staticmethod
    def save_offender_image():
        VideoMaskDetection.count += 1
        cv2.imwrite(f"captures/capture{VideoMaskDetection.count}.png", last_read_frame)
        VideoMaskDetection.flag = False

    def start_mask_detection(self, frame):
        """
        Unpack locations and predictions of faces and draw box on faces
        :param frame: frame to be passed for detections
        """
        global last_read_frame
        try:
            (v_locations, v_predictions) = self.detect_and_predict(frame, self.faceModel, self.maskModel)
        except TypeError:
            pass
        else:
            for (box, pred) in zip(v_locations, v_predictions):
                # unpack the bounding box and predictions
                (startX, startY, endX, endY) = box
                (mask, withoutMask) = pred
                label = "Mask" if mask > withoutMask else "No Mask"
                color = (0, 255, 0) if label == "Mask" else (0, 0, 255)
                label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

                if withoutMask * 100 > 95:
                    pygame.mixer.music.play()
                    time.sleep(0.01)
                    cv2.imwrite("captures/last_capture.png", frame)
                    last_read_frame = frame
                    captured_frame = PhotoImage(file='../captures/last_capture.png')
                    VideoMaskDetection.captured_img = captured_frame
                    Interface.canvas.create_image(150, 150, image=captured_frame)
                    Interface.window.update_idletasks()
                    Interface.window.update()
                    VideoMaskDetection.flag = True

                cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
                cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
            cv2.imshow("Camera Feed", frame)

    def start_video_stream(self, stream_source):
        """
        Starts a video stream using a camera source
        :param stream_source: Sets the stream source (camera source) of the stream.
                                stream_source = 0 stream using system webcam,
                                stream_source = 1, 2, 3 .. : stream using connected camera/camera's.
        """
        vs = cv2.VideoCapture(stream_source)
        time.sleep(2.0)
        Interface.update_progress_bar(100)
        Interface.update_info_text("Press 'q' to quit window, press 's' to send notification of last detection")
        while True:
            frame_exist, frame = vs.read()
            if frame_exist:
                frame = imutils.resize(frame, width=400)
                self.start_mask_detection(frame=frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    Interface.canvas.create_image(150, 150, image=VideoMaskDetection.captured_img)
                    Interface.update_progress_bar(0)
                    Interface.update_info_text("")
                    break
                elif key == ord("s"):
                    Notification.notify(show_messagebox=False)

        vs.release()
        cv2.destroyAllWindows()

    def start_video_capture(self, path):
        """
        Starts a video capture from a video file and applies face-mask detection on each frame
        :param path: specifies the path of the video to capture
        """
        vc = cv2.VideoCapture(path)
        if not vc.isOpened():
            Interface.update_progress_bar(80)
            messagebox.showerror(title="Error loading Video", message=f"The video could not be loaded, Please check the"
                                                                      f" path and try again {path}!")
        Interface.update_progress_bar(100)
        Interface.update_info_text("Press 'q' to quit window, press 's' to send notification of last detection")

        while True:
            frame_exists, frame = vc.read()
            if frame_exists:
                pass
            else:
                Interface.update_progress_bar(0)
                break
            self.start_mask_detection(frame=frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                Interface.update_progress_bar(0)
                Interface.update_info_text("")
                break

        cv2.destroyAllWindows()
        vc.release()
