import os

import cv2
import easyocr
from PIL import Image
import numpy as np

os.environ['CUDA_LAUNCH_BLOCKING'] = "1"


class License_Recognizer:
    def __init__(self) -> None:
        self.reader_bn = easyocr.Reader(['bn'])
        self.reader_en = easyocr.Reader(['en'])
        self.INPUT_WIDTH = 640
        self.INPUT_HEIGHT = 640
        self.onnx_weight = "weight\\best.onnx"
        self.net = cv2.dnn.readNetFromONNX(self.onnx_weight)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    # predictions flow with return result
    def get_license_number(self, img, ):
        # step-1: detections
        input_image, detections = self.get_detections(img, self.net)

        # step-2: NMS
        boxes_np, confidences_np, index = self.non_maximum_supression(input_image, detections)

        # step-3: Drawings
        result_img, texts = self.drawings(img, boxes_np, confidences_np, index)
        return result_img, texts, boxes_np

    def get_detections(self, img, net):
        # 1.CONVERT IMAGE TO YOLO FORMAT
        image = img.copy()
        row, col, d = image.shape

        max_rc = max(row, col)
        input_image = np.zeros((max_rc, max_rc, 3), dtype=np.uint8)
        input_image[0:row, 0:col] = image

        # 2. GET PREDICTION FROM YOLO MODEL
        blob = cv2.dnn.blobFromImage(input_image, 1 / 255, (self.INPUT_WIDTH, self.INPUT_HEIGHT), swapRB=True,
                                     crop=False)
        net.setInput(blob)
        preds = net.forward()

        detections = preds[0]

        return input_image, detections

    def non_maximum_supression(self, input_image, detections):
        # 3. FILTER DETECTIONS BASED ON CONFIDENCE AND PROBABILIY SCORE

        # center x, center y, w , h, conf, proba
        boxes = []
        confidences = []

        image_w, image_h = input_image.shape[:2]
        x_factor = image_w / self.INPUT_WIDTH
        y_factor = image_h / self.INPUT_HEIGHT

        for i in range(len(detections)):
            row = detections[i]
            confidence = row[4]  # confidence of detecting license plate
            if confidence > 0.4:
                class_score = row[5]  # probability score of license plate
                if class_score > 0.25:
                    cx, cy, w, h = row[0:4]

                    left = int((cx - 0.5 * w) * x_factor)
                    top = int((cy - 0.5 * h) * y_factor)
                    width = int(w * x_factor)
                    height = int(h * y_factor)
                    box = np.array([left, top, width, height])

                    confidences.append(confidence)
                    boxes.append(box)

        # 4.1 CLEAN
        boxes_np = np.array(boxes).tolist()
        confidences_np = np.array(confidences).tolist()

        # 4.2 NMS
        index = cv2.dnn.NMSBoxes(boxes_np, confidences_np, 0.25, 0.45)

        return boxes_np, confidences_np, index

    def drawings(self, image, boxes_np, confidences_np, index):
        # 5. Drawings
        texts = []
        for ind in index:
            x, y, w, h = boxes_np[ind]
            bb_conf = confidences_np[ind]
            conf_text = 'plate: {:.0f}%'.format(bb_conf * 100)
            license_text = self.extract_text(image, boxes_np[ind])
            texts.append(license_text)

            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.rectangle(image, (x, y - 30), (x + w, y), (0, 255, 0), -1)
            cv2.rectangle(image, (x, y + h), (x + w, y + h + 25), (0, 0, 255), -1)

            cv2.putText(image, conf_text, (x, y - 10), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(image, license_text, (x, y + h + 27), cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 255, 0), 1)

        return image, texts

    # extrating text
    def extract_text(self, image, bbox):
        x, y, w, h = bbox
        roi = image[y:y + h, x:x + w]

        if 0 in roi.shape:
            return 'no number'

        else:
            # extract text using EasyOCR
            result_bn = self.reader_bn.readtext(roi)
            result_en = self.reader_en.readtext(roi)

            text_bn = ' '.join([res[1] for res in result_bn])
            text_bn = text_bn.strip()

            text_en = ' '.join([res[1] for res in result_en])
            text_en = text_en.strip()

            if not text_bn and text_en:
                return "E"+text_en
            if not text_en and text_bn:
                return "B"+text_bn

            if len(text_bn) > len(text_en):
                return "B"+text_bn
            else:
                return "E"+text_en
