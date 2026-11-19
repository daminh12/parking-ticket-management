import pytest
from PyQt5.QtWidgets import QApplication
from main import Main
from tv4.camera_demo import DemoCapture, DemoImageStore, DemoOCR, DemoUI


def test_demo_runs_without_group_ui_ocr_or_model_files():
    app = QApplication.instance() or QApplication([])
    store = DemoImageStore()
    window = Main(ocr=DemoOCR(), store=store, ui_factory=DemoUI,
                  capture_factory=DemoCapture, start_timer=False)
    window.show()
    app.processEvents()
    window.start_predict()
    assert window.ui.label_digits.text() == "29A - 12345"
    window.ui.button_check_in.click()
    assert len(store.records) == 1
    window.ui.button_check_out.click()
    assert not store.records
    window.close()
    assert not window.cap.isOpened()


def test_unfinished_group_ui_has_actionable_message():
    app = QApplication.instance() or QApplication([])
    class UnfinishedUI:
        def __init__(self, window):
            self.setupUi(window)
    with pytest.raises(RuntimeError, match="--demo"):
        Main(ui_factory=UnfinishedUI)
