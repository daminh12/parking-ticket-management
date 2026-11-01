from ultralytics import YOLO
import cv2
import numpy as np

class OcrPlate:
    # Để mục khởi tạo này riêng với set_data vì load model quá nặng
    def __init__(self, path_model_detect_plate, path_model_ocr):
        self.model_license = YOLO(path_model_detect_plate)
        self.model_ocr = YOLO(path_model_ocr)

    # Đặt data đầu vào chính là ảnh cần dự đoán
    def set_data(self, imgage_input):
        self.image_input = imgage_input.copy() # Tránh việc bị thay đổi đầu vào
        self.image_output = imgage_input # Ảnh đầu ra sau khi vẽ các bounding box và các nhãn của từng biển
        self.digit_out = 'unknow' # Kí tự của biển cuối cùng được giải mã
        self.box_xyxy = None # Chứa các thông số tọa độ của bouding boxes (tensor 2D)
        self.detect_plate_ocr() # Chạy luôn hàm để detect luôn
