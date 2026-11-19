"""TV4 integration example for the reference project's existing TV1-TV3 API.

Run from the team repository after its UI, OCR and storage modules are complete.
This is a camera/OCR demo; reservation, history and real pricing belong to WBS.
"""
import argparse
import logging
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow

BASE_DIR = Path(__file__).resolve().parent
DEMO_FEE_VND = 3000  # Reference demo only; replace with TV3's agreed pricing service.
LOGGER = logging.getLogger(__name__)


class Main(QMainWindow):
    """Own the real Qt window so Qt dispatches closeEvent to this class."""

    def __init__(self, source=None, *, ocr=None, store=None,
                 ui_factory=None, capture_factory=None, start_timer=True):
        super().__init__()
        self.cap = None
        self.timer = QTimer(self)
        self.digit_plate = None
        self.image_in = None

        if ui_factory is None:
            from main_ui import Ui_MainWindow
            ui_factory = Ui_MainWindow
        # Both the reference UI and the current team's constructor accept a window.
        try:
            self.ui = ui_factory(self)
        except AttributeError as error:
            raise RuntimeError("UI TV1 chưa hoàn thiện. Dùng --demo để kiểm tra phần TV4.") from error
        required = (
            "button_check_in", "button_check_out", "label_main", "label_in",
            "label_plate", "label_digits", "label_time", "label_price", "label_status",
        )
        missing = [name for name in required if not hasattr(self.ui, name)]
        if missing:
            raise RuntimeError("TV1 UI is incomplete; missing: " + ", ".join(missing))

        if store is None:
            import check_and_save_img as storage_module
            # Compatibility with TV3's existing module-level path_root variable.
            storage_module.path_root = str(BASE_DIR / "image_data")
            store = storage_module.CheckAndSaveImg()
        self.OJ = store

        if source is None:
            source = str(BASE_DIR / "test.MOV")
        elif isinstance(source, (str, Path)):
            source = str(source)
            if not Path(source).is_absolute():
                source = str(BASE_DIR / source)
        if capture_factory is None:
            capture_factory = cv2.VideoCapture
        self.cap = capture_factory(source)
        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"Cannot open video/camera: {source}")

        try:
            if ocr is None:
                try:
                    from OcrPlate import OcrPlate
                except ImportError as error:
                    raise RuntimeError("Module OCR TV2 chưa hoàn thiện. Dùng --demo để kiểm tra TV4.") from error
                plate_path = BASE_DIR / "model" / "best_plate.pt"
                ocr_path = BASE_DIR / "model" / "best_ocr.pt"
                for path in (plate_path, ocr_path):
                    if not path.is_file():
                        raise FileNotFoundError(f"Missing model: {path}")
                ocr = OcrPlate(path_model_detect_plate=str(plate_path),
                               path_model_ocr=str(ocr_path))
            self.ocr_plate = ocr
            self.ui.button_check_in.clicked.connect(self.check_in)
            self.ui.button_check_out.clicked.connect(self.check_out)
            self.timer.timeout.connect(self.start_predict)
            self._clear_detection("Chờ nhận diện biển số")
            if start_timer:
                self.timer.start(50)  # Trigger interval, not a guaranteed inference FPS.
        except Exception:
            self.cap.release()
            raise

    def convert_qimg(self, image):
        """Accept uint8 OpenCV BGR and return an independent RGB QImage."""
        if (not isinstance(image, np.ndarray) or image.dtype != np.uint8
                or image.ndim != 3 or image.shape[2] != 3 or image.size == 0):
            raise ValueError("Expected a nonempty uint8 HxWx3 BGR image")
        rgb = np.ascontiguousarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        height, width, _ = rgb.shape
        return QImage(rgb.data, width, height, int(rgb.strides[0]),
                      QImage.Format_RGB888).copy()

    def _show_image(self, label, image):
        pixmap = QPixmap.fromImage(self.convert_qimg(image))
        label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio,
                                      Qt.SmoothTransformation))

    def _clear_detection(self, message):
        self.digit_plate = None
        self.image_in = None
        self.ui.button_check_in.setEnabled(False)
        self.ui.button_check_out.setEnabled(False)
        for name in ("label_plate", "label_digits", "label_in", "label_time", "label_price"):
            getattr(self.ui, name).setText("--")
        self.ui.label_status.setText(message)

    @staticmethod
    def _valid_plate(value):
        # Keep TV2's display key (including spaces and hyphens) unchanged for TV3.
        return (isinstance(value, str) and bool(value.strip())
                and value.strip().lower() not in {"unknow", "unknown", "none"}
                and bool(re.fullmatch(r"[A-Za-z0-9 -]+", value))
                and any(character.isdigit() for character in value))

    def _refresh_record(self):
        exists = self.OJ.check_exists(label=self.digit_plate)
        if exists:
            record = self.OJ.get_data(label=self.digit_plate)
            if (not isinstance(record, tuple) or len(record) != 2
                    or not isinstance(record[1], np.ndarray) or record[1].size == 0):
                raise ValueError("Stored vehicle image is missing or unreadable")
            timestamp, image = record
            self._show_image(self.ui.label_in, image)
            self.ui.label_time.setText(str(timestamp))
            self.ui.label_price.setText(f"{DEMO_FEE_VND} VND (demo)")
            self.ui.label_status.setText("Đã trong bãi")
        else:
            self.ui.label_in.setText("Xe chưa vào bãi")
            self.ui.label_time.setText("--")
            self.ui.label_price.setText("--")
            self.ui.label_status.setText("Xe chưa vào bãi")
        self.ui.button_check_in.setEnabled(not exists)
        self.ui.button_check_out.setEnabled(exists)

    def check_in(self):
        if self.digit_plate is None or self.image_in is None:
            return
        try:
            if not self.OJ.check_exists(label=self.digit_plate):
                self.OJ.save_image(label=self.digit_plate, image_array=self.image_in.copy())
                if not self.OJ.check_exists(label=self.digit_plate):
                    raise OSError("Vehicle record was not saved")
            self._refresh_record()
        except Exception as error:
            LOGGER.exception("Check-in failed")
            self._clear_detection(f"Lỗi lưu ảnh: {error}")

    def check_out(self):
        if self.digit_plate is None:
            return
        try:
            if self.OJ.check_exists(label=self.digit_plate):
                self.OJ.delete_image(label=self.digit_plate)
                if self.OJ.check_exists(label=self.digit_plate):
                    raise OSError("Vehicle record was not deleted")
            self._refresh_record()
        except Exception as error:
            LOGGER.exception("Check-out failed")
            self._clear_detection(f"Lỗi xóa ảnh: {error}")

    def start_predict(self):
        try:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                self.timer.stop()
                self.cap.release()
                self._clear_detection("Video đã kết thúc hoặc mất kết nối camera")
                return
            original = frame.copy()
            # Preserve TV2's existing keyword, including its spelling.
            self.ocr_plate.set_data(imgage_input=frame)
            self._show_image(self.ui.label_main, self.ocr_plate.image_output)
            digits = self.ocr_plate.digit_out
            if not self._valid_plate(digits):
                self._clear_detection("Không nhận dạng được")
                return
            boxes = self.ocr_plate.box_xyxy
            if hasattr(boxes, "detach"):
                boxes = boxes.detach().cpu().numpy()
            boxes = np.asarray(boxes)
            # Reference OCR does not identify which box produced digit_out.
            # Reject ambiguity instead of attaching a plate to the wrong vehicle.
            if boxes.shape != (1, 4):
                self._clear_detection("Cần đúng một biển số trong khung hình")
                return
            if not np.all(np.isfinite(boxes)):
                self._clear_detection("Tọa độ biển số không hợp lệ")
                return
            height, width = original.shape[:2]
            x0, y0, x1, y1 = map(int, boxes[0])
            x0, x1 = max(0, min(width, x0)), max(0, min(width, x1))
            y0, y1 = max(0, min(height, y0)), max(0, min(height, y1))
            if x1 <= x0 or y1 <= y0:
                self._clear_detection("Ảnh cắt biển số không hợp lệ")
                return
            self.digit_plate = digits
            self.image_in = original
            self._show_image(self.ui.label_plate, original[y0:y1, x0:x1])
            self.ui.label_digits.setText(digits)
            self._refresh_record()
        except Exception as error:
            LOGGER.exception("Recognition pipeline failed")
            self.timer.stop()
            self.cap.release()
            self._clear_detection(f"Lỗi xử lý: {error}")

    def release_resources(self):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()

    def closeEvent(self, event):
        self.release_resources()
        super().closeEvent(event)


def run(argv=None):
    parser = argparse.ArgumentParser(description="TV4 camera/OCR integration demo")
    parser.add_argument("--source", default=None, help="Video path or camera number, e.g. 0")
    parser.add_argument("--demo", action="store_true", help="Synthetic camera/OCR; no real model or stored user data")
    args = parser.parse_args(argv)
    if args.demo and args.source is not None:
        parser.error("--demo dùng camera mô phỏng; không dùng cùng --source")
    source = args.source
    if source is not None and source.isdecimal():
        source = int(source)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    try:
        if args.demo:
            from tv4.camera_demo import DemoUI, DemoCapture, DemoOCR, DemoImageStore
            window = Main(ocr=DemoOCR(), store=DemoImageStore(),
                          ui_factory=DemoUI, capture_factory=DemoCapture)
        else:
            window = Main(source=source)
    except Exception as error:
        print(f"Không thể khởi động: {error}", file=sys.stderr)
        return 1
    window.show()
    app.aboutToQuit.connect(window.release_resources)
    return app.exec_()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(run())
