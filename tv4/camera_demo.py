"""Synthetic camera and OCR for exercising TV4 without TV1/TV2 modules."""
from datetime import datetime, timedelta, timezone
import cv2
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QGridLayout, QLabel, QPushButton,
                            QVBoxLayout, QWidget)


class DemoUI:
    def __init__(self, window):
        window.setWindowTitle("TV4 — Camera minh họa")
        window.resize(1120, 760)
        central = QWidget(window)
        window.setCentralWidget(central)
        layout = QVBoxLayout(central)
        banner = QLabel("CHẾ ĐỘ MINH HỌA — biển số giả lập, ảnh chỉ lưu trong phiên chạy")
        banner.setStyleSheet("background:#fff1c2;color:#553600;padding:12px;font-weight:bold")
        banner.setFixedHeight(48)
        layout.addWidget(banner)
        grid = QGridLayout()
        layout.addLayout(grid)
        for index, (name, title) in enumerate((
            ("label_main", "Camera"), ("label_in", "Ảnh khi vào"),
            ("label_plate", "Biển số"), ("label_digits", "Kết quả"),
            ("label_time", "Giờ vào"), ("label_price", "Phí minh họa"),
            ("label_status", "Trạng thái"),
        )):
            box = QVBoxLayout()
            box.addWidget(QLabel(title))
            label = QLabel("--")
            label.setMinimumSize(240, 180 if index < 2 else (140 if index == 2 else 55))
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("border:1px solid #cbd5e1;background:#f8fafc;padding:6px")
            setattr(self, name, label)
            box.addWidget(label)
            grid.addLayout(box, index // 2, index % 2)
        self.button_check_in = QPushButton("Xác nhận vào")
        self.button_check_out = QPushButton("Xác nhận ra")
        layout.addWidget(self.button_check_in)
        layout.addWidget(self.button_check_out)


class DemoCapture:
    def __init__(self, source=None):
        self.opened = True

    def isOpened(self):
        return self.opened

    def read(self):
        if not self.opened:
            return False, None
        image = np.full((360, 640, 3), (60, 45, 25), dtype=np.uint8)
        cv2.rectangle(image, (160, 180), (480, 260), (255, 255, 255), -1)
        cv2.putText(image, "29A-12345", (170, 235), cv2.FONT_HERSHEY_SIMPLEX,
                    1.7, (0, 0, 0), 3)
        cv2.putText(image, "SIMULATED CAMERA / OCR", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 220, 255), 2)
        return True, image

    def release(self):
        self.opened = False


class DemoOCR:
    def set_data(self, imgage_input):
        self.image_input = imgage_input.copy()
        self.image_output = imgage_input.copy()
        self.digit_out = "29A - 12345"
        self.box_xyxy = np.array([[160, 180, 480, 260]])


class DemoImageStore:
    def __init__(self):
        self.records = {}

    def check_exists(self, label):
        return label in self.records

    def save_image(self, label, image_array):
        if label not in self.records:
            self.records[label] = (
                datetime.now(timezone(timedelta(hours=7))).strftime("%H:%M:%S %d-%m-%Y"), image_array.copy()
            )

    def get_data(self, label):
        timestamp, image = self.records[label]
        return timestamp, image.copy()

    def delete_image(self, label):
        self.records.pop(label, None)
