import pytest
from PyQt5.QtWidgets import QApplication
from tv4.parking import DemoGateway, ConflictError
from tv4.portal import UserPortal


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def portal(app):
    window = UserPortal(DemoGateway(), demo=True, confirm_cancel=lambda: True)
    yield window
    window.close()


def select_space(window, space_id):
    for row in range(window.space_table.rowCount()):
        if window.space_table.item(row, 0).text() == space_id:
            window.space_table.selectRow(row)
            return
    raise AssertionError(f"Space {space_id} not visible")


def test_filter_and_empty_result_state(portal):
    portal.zone_filter.setCurrentText("B")
    assert portal.space_table.rowCount() == 2
    portal.state_filter.setCurrentText("Đang sử dụng")
    assert portal.space_table.rowCount() == 0
    assert not portal.reserve_button.isEnabled()
    assert "0 chỗ" in portal.summary.text()


def test_clicking_space_map_selects_same_space_in_table(portal):
    portal.space_map.itemAt(0).widget().click()
    assert portal.space_table.item(portal.space_table.currentRow(), 0).text() == "A01"
    assert portal.reserve_button.isEnabled()


def test_reserve_then_cancel_via_real_qt_buttons(portal):
    select_space(portal, "A01")
    portal.reserve_plate.setText("29a-12345")
    portal.reserve_button.click()
    assert portal.reservation_table.rowCount() == 1
    assert portal.reservation_table.item(0, 2).text() == "29A12345"
    portal.reservation_table.selectRow(0)
    portal.cancel_button.click()
    assert portal.reservation_table.item(0, 4).text() == "Đã hủy"
    assert not portal.cancel_button.isEnabled()


def test_cancel_confirmation_can_be_declined(portal):
    record = portal.gateway.reserve("A01", "29A12345")
    portal.reload()
    portal.reservation_table.selectRow(0)
    portal.confirm_cancel = lambda: False
    portal.cancel_button.click()
    assert portal.gateway.list_reservations()[0].id == record.id
    assert portal.gateway.list_reservations()[0].status == "Đang giữ chỗ"


def test_invalid_reservation_does_not_create_record(portal):
    select_space(portal, "A01")
    portal.reserve_plate.setText("../wrong")
    portal.reserve_button.click()
    assert portal.reservation_table.rowCount() == 0
    assert "chưa hợp lệ" in portal.message.text()


def test_occupied_selection_cannot_be_reserved(portal):
    select_space(portal, "A03")
    assert not portal.reserve_button.isEnabled()


def test_lookup_normalization_and_completed_history(portal):
    portal.lookup_plate.setText("36x1 - 4359")
    portal.lookup_button.click()
    assert portal.history_table.rowCount() == 1
    assert portal.history_table.item(0, 6).text() == "Đã kết thúc"
    assert portal.history_table.item(0, 5).text() == "3000 VND"


def test_invalid_lookup_clears_previous_results(portal):
    portal.lookup_plate.setText("29A11111")
    portal.lookup()
    assert portal.history_table.rowCount() == 1
    portal.lookup_plate.clear()
    portal.lookup()
    assert portal.history_table.rowCount() == 0
    assert "Vui lòng nhập" in portal.message.text()


def test_no_results_is_different_from_service_error(portal):
    portal.lookup_plate.setText("29A99999")
    portal.lookup()
    assert portal.lookup_status.text() == "Không có kết quả."
    def fail(plate):
        raise OSError("internal DB path that must not be shown")
    portal.gateway.lookup = fail
    portal.lookup()
    assert "Chưa thể tra cứu" in portal.lookup_status.text()
    assert "Không thể kết nối" in portal.message.text()
    assert "internal DB path" not in portal.message.text()
    assert portal.lookup_button.isEnabled()


def test_reservation_conflict_is_shown_without_false_success(portal):
    select_space(portal, "A01")
    portal.reserve_plate.setText("29A12345")
    def conflict(space_id, plate):
        raise ConflictError("Chỗ đã được người khác đặt.")
    portal.gateway.reserve = conflict
    portal.reserve_button.click()
    assert "người khác" in portal.message.text()
    assert portal.reservation_table.rowCount() == 0


def test_failed_reload_clears_stale_bookable_spaces(portal):
    select_space(portal, "A01")
    def fail():
        raise OSError("service offline")
    portal.gateway.list_spaces = fail
    assert not portal.reload()
    assert portal.space_table.rowCount() == 0
    assert not portal.reserve_button.isEnabled()
