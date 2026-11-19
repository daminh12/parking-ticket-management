"""TV4 desktop reservation and plate-lookup frontend.

Run `python -m tv4.portal` for an explicitly labelled, in-memory demo. Supply a
ParkingGateway implementation to UserPortal for the team's real integration.
"""
import logging
import sys
from datetime import timedelta, timezone
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView, QApplication, QComboBox, QFormLayout, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from .parking import DemoGateway, ParkingError, ParkingGateway, SpaceState, normalize_plate

LOGGER = logging.getLogger(__name__)
DISPLAY_ZONE = timezone(timedelta(hours=7))


class UserPortal(QMainWindow):
    def __init__(self, gateway: ParkingGateway, *, demo=False, confirm_cancel=None):
        super().__init__()
        self.gateway = gateway
        self.demo = demo
        self.confirm_cancel = confirm_cancel or self._confirm_cancel
        self.spaces = ()
        self.setWindowTitle("TV4 — Đặt chỗ và tra cứu")
        self.resize(1120, 760)
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        title = QLabel("Bãi đỗ xe · Đặt chỗ và tra cứu")
        title.setObjectName("title")
        layout.addWidget(title)
        if demo:
            banner = QLabel("CHẾ ĐỘ MINH HỌA · Dữ liệu mẫu, không lưu sau khi đóng. "
                            "Chưa áp dụng tài khoản và bảng giá thực tế.")
            banner.setObjectName("demo")
            banner.setWordWrap(True)
            layout.addWidget(banner)
        self.message = QLabel("Chọn chỗ trống để bắt đầu.")
        self.message.setWordWrap(True)
        layout.addWidget(self.message)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self._build_spaces()
        self._build_reservations()
        self._build_lookup()
        self.setStyleSheet("""
            QMainWindow { background:#f1f5f9; }
            QLabel#title { font-size:24px; font-weight:700; color:#0f172a; padding:12px; }
            QLabel#demo { background:#fef3c7; color:#713f12; padding:12px; }
            QTableWidget { background:white; gridline-color:#e2e8f0; }
            QHeaderView::section { background:#e2e8f0; padding:9px; border:0; }
            QPushButton { background:#1d4ed8; color:white; border:0; padding:10px 16px; }
            QPushButton:disabled { background:#94a3b8; }
            QLineEdit, QComboBox { padding:8px; background:white; border:1px solid #cbd5e1; }
            QTabBar::tab { padding:12px 18px; }
        """)
        self.reload()

    @staticmethod
    def _table(headers):
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def _build_spaces(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        filters = QHBoxLayout()
        self.zone_filter = QComboBox()
        self.zone_filter.addItem("Tất cả khu")
        self.state_filter = QComboBox()
        self.state_filter.addItems(["Tất cả trạng thái"] + [s.value for s in SpaceState])
        self.type_filter = QComboBox()
        self.type_filter.addItems(["Tất cả loại xe", "Ô tô", "Xe máy"])
        self.reload_button = QPushButton("Tải lại")
        for widget in (self.zone_filter, self.state_filter, self.type_filter, self.reload_button):
            filters.addWidget(widget)
        layout.addLayout(filters)
        self.summary = QLabel()
        layout.addWidget(self.summary)
        layout.addWidget(QLabel("Trống · Đã đặt · Đang sử dụng · Ngừng hoạt động"))
        self.space_map = QGridLayout()
        layout.addLayout(self.space_map)
        self.space_table = self._table(["Mã chỗ", "Khu", "Loại xe", "Trạng thái"])
        self.space_table.setMinimumHeight(150)
        layout.addWidget(self.space_table)
        form = QFormLayout()
        self.reserve_plate = QLineEdit()
        self.reserve_plate.setMaxLength(64)
        self.reserve_plate.setPlaceholderText("Ví dụ: 29A-12345 hoặc 36X1-4359")
        form.addRow("Biển số xe:", self.reserve_plate)
        layout.addLayout(form)
        self.reserve_button = QPushButton("Xác nhận đặt chỗ đã chọn")
        self.reserve_button.setEnabled(False)
        layout.addWidget(self.reserve_button)
        self.tabs.addTab(page, "Chỗ đỗ")
        self.reload_button.clicked.connect(self.reload)
        self.reserve_button.clicked.connect(self.reserve_selected)
        self.space_table.itemSelectionChanged.connect(self._update_selection)
        for combo in (self.zone_filter, self.state_filter, self.type_filter):
            combo.currentTextChanged.connect(self._filter_spaces)

    def _build_reservations(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Chỉ hiển thị đặt chỗ của người dùng hiện tại."))
        self.reservation_table = self._table(["Mã đặt", "Chỗ", "Biển số", "Tạo lúc", "Trạng thái"])
        layout.addWidget(self.reservation_table)
        self.cancel_button = QPushButton("Hủy đặt chỗ đã chọn")
        self.cancel_button.setEnabled(False)
        layout.addWidget(self.cancel_button)
        self.tabs.addTab(page, "Đặt chỗ của tôi")
        self.cancel_button.clicked.connect(self.cancel_selected)
        self.reservation_table.itemSelectionChanged.connect(self._update_selection)

    def _build_lookup(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        controls = QHBoxLayout()
        self.lookup_plate = QLineEdit()
        self.lookup_plate.setMaxLength(64)
        self.lookup_plate.setPlaceholderText("Nhập biển số để tra cứu")
        self.lookup_button = QPushButton("Tra cứu")
        controls.addWidget(self.lookup_plate)
        controls.addWidget(self.lookup_button)
        layout.addLayout(controls)
        if self.demo:
            layout.addWidget(QLabel("Mẫu demo: 29A-11111 đang gửi; 36X1-4359 đã kết thúc."))
        self.lookup_status = QLabel("Nhập biển số để xem phiên gửi được phép truy cập.")
        layout.addWidget(self.lookup_status)
        self.history_table = self._table(["Mã lượt", "Biển số", "Chỗ", "Giờ vào", "Giờ ra", "Phí", "Trạng thái"])
        layout.addWidget(self.history_table)
        self.tabs.addTab(page, "Tra cứu và lịch sử")
        self.lookup_button.clicked.connect(self.lookup)
        self.lookup_plate.returnPressed.connect(self.lookup)

    def _notice(self, text, error=False):
        self.message.setText(text)
        self.message.setStyleSheet("padding:8px;color:" + ("#b91c1c" if error else "#166534"))

    def _failure(self, error):
        if isinstance(error, ParkingError):
            self._notice(str(error), error=True)
        else:
            LOGGER.exception("Parking service request failed")
            self._notice("Không thể kết nối dịch vụ. Vui lòng thử lại.", error=True)

    @staticmethod
    def _fill(table, rows):
        table.setRowCount(0)
        for row_number, row in enumerate(rows):
            table.insertRow(row_number)
            for column, value in enumerate(row):
                table.setItem(row_number, column, QTableWidgetItem(str(value)))

    def reload(self):
        try:
            self.spaces = self.gateway.list_spaces()
            records = self.gateway.list_reservations()
            selected_zone = self.zone_filter.currentText()
            self.zone_filter.blockSignals(True)
            self.zone_filter.clear()
            self.zone_filter.addItems(["Tất cả khu"] + sorted({s.zone for s in self.spaces}))
            self.zone_filter.setCurrentText(selected_zone)
            self.zone_filter.blockSignals(False)
            self._filter_spaces()
            self._fill(self.reservation_table, [
                (r.id, r.space_id, r.plate, r.created_at.astimezone(DISPLAY_ZONE).strftime("%d/%m/%Y %H:%M"), r.status)
                for r in records
            ])
            self._update_selection()
            return True
        except Exception as error:
            self.spaces = ()
            self.space_table.setRowCount(0)
            self._render_map(())
            self.reservation_table.setRowCount(0)
            self.summary.setText("Chưa tải được dữ liệu chỗ đỗ.")
            self._update_selection()
            self._failure(error)
            return False

    def _filter_spaces(self):
        spaces = [s for s in self.spaces
                  if (self.zone_filter.currentIndex() == 0 or s.zone == self.zone_filter.currentText())
                  and (self.state_filter.currentIndex() == 0 or s.state.value == self.state_filter.currentText())
                  and (self.type_filter.currentIndex() == 0 or s.vehicle_type == self.type_filter.currentText())]
        self._fill(self.space_table, [(s.id, s.zone, s.vehicle_type, s.state.value) for s in spaces])
        self._render_map(spaces)
        self.summary.setText(f"Hiển thị {len(spaces)} chỗ · "
                             f"{sum(s.state == SpaceState.FREE for s in spaces)} chỗ trống")
        self._update_selection()

    def _render_map(self, spaces):
        while self.space_map.count():
            item = self.space_map.takeAt(0)
            item.widget().hide()
            item.widget().deleteLater()
        colors = {
            SpaceState.FREE: "#dcfce7", SpaceState.RESERVED: "#fef3c7",
            SpaceState.OCCUPIED: "#fee2e2", SpaceState.CLOSED: "#e2e8f0",
        }
        for index, space in enumerate(spaces):
            button = QPushButton(f"{space.id} · {space.vehicle_type}\n{space.state.value}")
            button.setStyleSheet(f"background:{colors[space.state]};color:#0f172a;"
                                 "border:1px solid #cbd5e1;padding:8px")
            button.clicked.connect(lambda checked=False, space_id=space.id: self._select_space(space_id))
            self.space_map.addWidget(button, index // 3, index % 3)

    def _select_space(self, space_id):
        for row in range(self.space_table.rowCount()):
            if self.space_table.item(row, 0).text() == space_id:
                self.space_table.selectRow(row)
                return

    def _update_selection(self):
        row = self.space_table.currentRow()
        item = self.space_table.item(row, 3)
        self.reserve_button.setEnabled(item is not None and item.text() == SpaceState.FREE.value)
        row = self.reservation_table.currentRow()
        item = self.reservation_table.item(row, 4)
        self.cancel_button.setEnabled(item is not None and item.text() == "Đang giữ chỗ")

    def reserve_selected(self):
        row = self.space_table.currentRow()
        item = self.space_table.item(row, 0)
        if item is None:
            self._notice("Vui lòng chọn một chỗ trống.", error=True)
            return
        self.reserve_button.setEnabled(False)
        try:
            plate = normalize_plate(self.reserve_plate.text())
            record = self.gateway.reserve(item.text(), plate)
        except Exception as error:
            self.reload()
            self._failure(error)
        else:
            refreshed = self.reload()
            self.reserve_plate.clear()
            if refreshed:
                self._notice(f"Đã đặt chỗ {record.space_id} cho xe {record.plate}.")
            self.tabs.setCurrentIndex(1)

    def _confirm_cancel(self):
        return QMessageBox.question(self, "Xác nhận hủy", "Bạn muốn hủy đặt chỗ đã chọn?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

    def cancel_selected(self):
        item = self.reservation_table.item(self.reservation_table.currentRow(), 0)
        if item is None:
            self._notice("Vui lòng chọn đặt chỗ cần hủy.", error=True)
            return
        reservation_id = item.text()
        if not self.confirm_cancel():
            return
        self.cancel_button.setEnabled(False)
        try:
            self.gateway.cancel(reservation_id)
        except Exception as error:
            self.reload()
            self._failure(error)
        else:
            if self.reload():
                self._notice("Đã hủy đặt chỗ.")

    def lookup(self):
        self.history_table.setRowCount(0)
        self.lookup_button.setEnabled(False)
        try:
            records = self.gateway.lookup(normalize_plate(self.lookup_plate.text()))
            self._fill(self.history_table, [
                (v.id, v.plate, v.space_id,
                 v.entered_at.astimezone(DISPLAY_ZONE).strftime("%d/%m/%Y %H:%M"),
                 v.exited_at.astimezone(DISPLAY_ZONE).strftime("%d/%m/%Y %H:%M") if v.exited_at else "--",
                 f"{v.fee_vnd} VND" if v.fee_vnd is not None else "Chưa kết thúc",
                 "Đã kết thúc" if v.exited_at else "Đang trong bãi")
                for v in records
            ])
            self.lookup_status.setText(f"Tìm thấy {len(records)} lượt gửi." if records else "Không có kết quả.")
            self._notice("Đã hoàn tất tra cứu.")
        except Exception as error:
            self.lookup_status.setText("Chưa thể tra cứu; hãy kiểm tra thông báo lỗi.")
            self._failure(error)
        finally:
            self.lookup_button.setEnabled(True)


def run():
    app = QApplication.instance() or QApplication(sys.argv)
    window = UserPortal(DemoGateway(), demo=True)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(run())
