"""Controller tests: real Qt/OpenCV; simulated camera, OCR and storage."""
import gc
import os
from pathlib import Path
import subprocess
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pytest
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton
from main import Main


@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])


class TestUI:
    __test__ = False

    def __init__(self, window):
        for name in ("label_main", "label_in", "label_plate", "label_digits",
                     "label_time", "label_price", "label_status"):
            label = QLabel(window)
            label.resize(200, 100)
            setattr(self, name, label)
        self.button_check_in = QPushButton(window)
        self.button_check_out = QPushButton(window)


class Camera:
    def __init__(self, opened=True):
        self.opened = opened
        self.frames = [np.zeros((40, 60, 3), dtype=np.uint8)]
        self.released = False

    def isOpened(self):
        return self.opened and not self.released

    def read(self):
        if self.frames:
            return True, self.frames.pop(0).copy()
        return False, None

    def release(self):
        self.released = True


class OCR:
    def __init__(self):
        self.digit_out = "29A - 12345"
        self.box_xyxy = np.array([[2, 3, 30, 20]])

    def set_data(self, imgage_input):
        self.image_input = imgage_input.copy()
        self.image_output = imgage_input.copy()


class Store:
    def __init__(self):
        self.records = {}
        self.saves = 0
        self.deletes = 0

    def check_exists(self, label):
        return label in self.records

    def save_image(self, label, image_array):
        self.saves += 1
        self.records[label] = ("10:00:00 09-11-2026", image_array.copy())

    def get_data(self, label):
        return self.records[label]

    def delete_image(self, label):
        self.deletes += 1
        del self.records[label]


@pytest.fixture
def controller(app):
    cap, ocr, store = Camera(), OCR(), Store()
    window = Main(ocr=ocr, store=store, ui_factory=TestUI,
                  capture_factory=lambda source: cap, start_timer=False)
    yield window, cap, ocr, store
    window.close()


def test_bgr_color_and_owned_image_memory(controller):
    window, *_ = controller
    bgr = np.zeros((4, 6, 3), dtype=np.uint8)
    bgr[:, :, 2] = 255
    result = window.convert_qimg(bgr[:, ::2])
    bgr[:] = 0
    del bgr
    gc.collect()
    assert result.width() == 3
    assert result.pixelColor(0, 0).getRgb() == (255, 0, 0, 255)


@pytest.mark.parametrize("image", [None, np.array([]),
                         np.zeros((3, 3), dtype=np.uint8),
                         np.zeros((3, 3, 3), dtype=float)])
def test_reject_invalid_image(controller, image):
    with pytest.raises(ValueError):
        controller[0].convert_qimg(image)


def test_no_detection_means_no_storage_actions(controller):
    window, _, _, store = controller
    window.check_in()
    window.check_out()
    assert store.saves == store.deletes == 0
    assert not window.ui.button_check_in.isEnabled()


def test_check_in_duplicate_and_check_out(controller):
    window, _, _, store = controller
    window.start_predict()
    assert window.ui.button_check_in.isEnabled()
    assert window.ui.label_price.text() == "--"
    window.ui.button_check_in.click()
    window.check_in()  # Defensive idempotence even when called programmatically.
    assert store.saves == 1
    assert window.ui.button_check_out.isEnabled()
    assert window.ui.label_status.text() == "Đã trong bãi"
    window.ui.button_check_out.click()
    window.check_out()
    assert store.deletes == 1
    assert not store.records
    assert window.ui.label_price.text() == "--"


def test_lost_detection_cannot_reuse_previous_plate(controller):
    window, cap, ocr, store = controller
    window.start_predict()
    cap.frames.append(np.zeros((40, 60, 3), dtype=np.uint8))
    ocr.digit_out = "unknow"
    window.start_predict()
    window.check_in()
    assert store.saves == 0
    assert window.digit_plate is None


def test_eof_stops_timer_releases_camera_and_disarms_buttons(controller):
    window, cap, _, _ = controller
    window.start_predict()
    window.timer.start(5000)
    window.start_predict()
    assert not window.timer.isActive()
    assert cap.released
    assert window.digit_plate is None


@pytest.mark.parametrize("boxes", [None, np.array([]),
                         np.array([[0, 0, 10, 10], [10, 10, 20, 20]]),
                         np.array([[10, 10, 1, 1]]),
                         np.array([[float('nan'), 0, 2, 2]])])
def test_invalid_or_ambiguous_boxes_cannot_save(controller, boxes):
    window, _, ocr, store = controller
    ocr.box_xyxy = boxes
    window.start_predict()
    window.check_in()
    assert store.saves == 0
    assert window.digit_plate is None


def test_clip_out_of_frame_coordinates(controller):
    window, _, ocr, _ = controller
    ocr.box_xyxy = np.array([[-10, -10, 1000, 1000]])
    window.start_predict()
    assert window.digit_plate == "29A - 12345"


def test_invalid_plate_cannot_become_storage_path(controller):
    window, _, ocr, store = controller
    ocr.digit_out = "../29A"
    window.start_predict()
    window.check_in()
    assert store.saves == 0


def test_corrupt_stored_image_is_reported(controller):
    window, _, ocr, store = controller
    store.records[ocr.digit_out] = ("timestamp", None)
    window.start_predict()
    assert "Lỗi xử lý" in window.ui.label_status.text()
    assert not window.ui.button_check_out.isEnabled()


def test_failed_save_does_not_report_success(controller):
    window, _, _, store = controller
    store.save_image = lambda **kwargs: None
    window.start_predict()
    window.check_in()
    assert "Lỗi lưu ảnh" in window.ui.label_status.text()
    assert not window.ui.button_check_out.isEnabled()


def test_ocr_failure_releases_camera(controller):
    window, cap, ocr, _ = controller
    def fail(**kwargs):
        raise RuntimeError("OCR unavailable")
    ocr.set_data = fail
    window.timer.start(5000)
    window.start_predict()
    assert not window.timer.isActive()
    assert cap.released
    assert "OCR unavailable" in window.ui.label_status.text()


def test_real_qt_close_event_releases_camera(controller, app):
    window, cap, _, _ = controller
    window.show()
    app.processEvents()
    window.timer.start(5000)
    assert window.close()
    app.processEvents()
    assert cap.released
    assert not window.timer.isActive()


def test_camera_open_failure_releases_resource(app):
    cap = Camera(opened=False)
    with pytest.raises(RuntimeError, match="Cannot open"):
        Main(ocr=OCR(), store=Store(), ui_factory=TestUI,
             capture_factory=lambda source: cap)
    assert cap.released


def test_model_load_failure_releases_camera(app, monkeypatch, tmp_path):
    import types
    import main as main_module
    cap = Camera()
    monkeypatch.setattr(main_module, "BASE_DIR", tmp_path)
    monkeypatch.setitem(sys.modules, "OcrPlate", types.SimpleNamespace(OcrPlate=object))
    with pytest.raises(FileNotFoundError, match="Missing model"):
        Main(store=Store(), ui_factory=TestUI, capture_factory=lambda source: cap)
    assert cap.released


def test_import_does_not_open_ui_or_require_ocr_modules():
    folder = str(Path(__file__).resolve().parents[1])
    result = subprocess.run([sys.executable, "-c", "import main; print('import-ok')"],
                            cwd=folder, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "import-ok"
