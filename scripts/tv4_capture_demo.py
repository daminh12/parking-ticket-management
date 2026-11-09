"""Reproduce TV4 demo screenshots and an optional scripted video.

Uses synthetic camera/OCR and in-memory parking data only. ffmpeg is required
only with --video. Run from the repository: python scripts/tv4_capture_demo.py.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from main import Main
from tv4.camera_demo import DemoCapture, DemoImageStore, DemoOCR, DemoUI
from tv4.parking import DemoGateway
from tv4.portal import UserPortal


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/tv4/evidence")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.video and shutil.which("ffmpeg") is None:
        parser.error("ffmpeg is required only when using --video")
    app = QApplication.instance() or QApplication([])
    window = UserPortal(DemoGateway(), demo=True, confirm_cancel=lambda: True)
    camera = None
    frame_count = 0
    try:
        with tempfile.TemporaryDirectory() as frames:
            frames = Path(frames)
            def capture(widget, name):
                nonlocal frame_count
                widget.resize(1120, 860)
                widget.show()
                app.processEvents()
                QTest.qWait(120)
                assert widget.grab().save(str(args.output / name))
                if args.video:
                    for _ in range(8):
                        app.processEvents()
                        assert widget.grab().save(str(frames / f"frame-{frame_count:04d}.png"))
                        frame_count += 1
                        QTest.qWait(60)

            capture(window, "portal-spaces.png")
            window.zone_filter.setCurrentText("B")
            assert window.space_table.rowCount() == 2
            capture(window, "portal-filter.png")
            window.zone_filter.setCurrentIndex(0)
            window.space_table.selectRow(0)
            window.reserve_plate.setText("29A-12345")
            window.reserve_button.click()
            assert window.reservation_table.rowCount() == 1
            capture(window, "portal-reservation.png")
            window.reservation_table.selectRow(0)
            window.cancel_button.click()
            assert window.reservation_table.item(0, 4).text() == "Đã hủy"
            capture(window, "portal-cancel.png")
            window.tabs.setCurrentIndex(2)
            window.lookup_plate.setText("36X1-4359")
            window.lookup_button.click()
            assert window.history_table.rowCount() == 1
            capture(window, "portal-history.png")
            window.lookup_plate.clear()
            window.lookup()
            assert window.history_table.rowCount() == 0
            capture(window, "portal-validation.png")
            window.hide()
            store = DemoImageStore()
            camera = Main(ocr=DemoOCR(), store=store, ui_factory=DemoUI,
                          capture_factory=DemoCapture, start_timer=False)
            camera.resize(1120, 860)
            camera.show()
            app.processEvents()
            camera.start_predict()
            camera.ui.button_check_in.click()
            assert camera.ui.label_status.text() == "Đã trong bãi"
            capture(camera, "camera-demo.png")
            camera.ui.button_check_out.click()
            assert not store.records
            camera.close()
            assert not camera.cap.isOpened()
            if args.video:
                subprocess.run([
                    "ffmpeg", "-y", "-loglevel", "error", "-framerate", "4",
                    "-i", str(frames / "frame-%04d.png"), "-c:v", "libvpx-vp9",
                    "-b:v", "500k", "-an", str(args.output / "tv4-demo.webm"),
                ], check=True)
    finally:
        if camera is not None:
            camera.close()
        window.close()
    print("PASS: filters, reserve, cancel, history, validation, camera entry/exit and close")


if __name__ == "__main__":
    run()
