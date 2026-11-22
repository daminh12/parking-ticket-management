from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from dataclasses import replace
import pytest
from tv4.parking import (
    AccessError, ConflictError, DemoFlatRate, DemoGateway,
    SpaceState, ValidationError, normalize_plate,
)


@pytest.mark.parametrize("raw,expected", [
    ("29A - 12345", "29A12345"), (" 29a-123.45 ", "29A12345"),
    ("36X1-4359", "36X14359"), ("30AB-12345", "30AB12345"),
])
def test_normalization(raw, expected):
    assert normalize_plate(raw) == expected


@pytest.mark.parametrize("raw", ["", " ", None, "12345678", "../29A12345",
                                  "29A' OR 1=1", "29A/12345", "A" * 100, "29A12"])
def test_invalid_input(raw):
    with pytest.raises(ValidationError):
        normalize_plate(raw)


def test_reserve_cancel_and_preserve_cancelled_history():
    gateway = DemoGateway()
    record = gateway.reserve("A01", "29A-12345")
    assert next(s for s in gateway.list_spaces() if s.id == "A01").state == SpaceState.RESERVED
    gateway.cancel(record.id)
    assert next(s for s in gateway.list_spaces() if s.id == "A01").state == SpaceState.FREE
    assert gateway.list_reservations()[0].status == "Đã hủy"
    with pytest.raises(ConflictError):
        gateway.cancel(record.id)


@pytest.mark.parametrize("space_id", ["A03", "A04"])
def test_cannot_reserve_occupied_or_closed_space(space_id):
    with pytest.raises(ConflictError):
        DemoGateway().reserve(space_id, "29A12345")


def test_unknown_space_is_validation_error():
    with pytest.raises(ValidationError):
        DemoGateway().reserve("missing", "29A12345")


def test_same_plate_cannot_hold_two_spaces_or_be_currently_parked():
    gateway = DemoGateway()
    gateway.reserve("A01", "29A12345")
    with pytest.raises(ConflictError):
        gateway.reserve("A02", "29A-12345")
    with pytest.raises(ConflictError):
        gateway.reserve("A02", "29A11111")


def test_two_competing_requests_only_one_wins():
    gateway = DemoGateway()
    def attempt(plate):
        try:
            gateway.reserve("A01", plate)
            return True
        except ConflictError:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, ["29A12345", "30A54321"]))
    assert outcomes.count(True) == 1
    assert len(gateway.list_reservations()) == 1


def test_cannot_cancel_another_owners_reservation():
    gateway = DemoGateway(owner_id="A")
    record = gateway.reserve("A01", "29A12345")
    gateway.owner_id = "B"  # Simulated second demo identity, not authentication.
    assert gateway.list_reservations() == ()
    with pytest.raises(AccessError):
        gateway.cancel(record.id)


def test_cannot_free_an_occupied_space_by_cancelling():
    gateway = DemoGateway()
    record = gateway.reserve("A01", "29A12345")
    gateway._spaces["A01"] = replace(gateway._spaces["A01"], state=SpaceState.OCCUPIED)
    with pytest.raises(ConflictError):
        gateway.cancel(record.id)
    assert gateway._spaces["A01"].state == SpaceState.OCCUPIED


def test_lookup_current_completed_and_no_result():
    gateway = DemoGateway()
    assert gateway.lookup("29a-11111")[0].exited_at is None
    assert gateway.lookup("36X1 - 4359")[0].fee_vnd == 3000
    assert gateway.lookup("29A99999") == ()
    gateway.owner_id = "OTHER"
    assert gateway.lookup("29A11111") == ()


def test_returned_records_are_immutable():
    from dataclasses import FrozenInstanceError
    with pytest.raises(FrozenInstanceError):
        DemoGateway().list_spaces()[0].state = SpaceState.CLOSED


def test_demo_fee_has_explicit_nonnegative_time_rule():
    start = datetime(2026, 11, 9, tzinfo=timezone.utc)
    tariff = DemoFlatRate()
    assert tariff.quote(start, start + timedelta(hours=1)) == 3000
    with pytest.raises(ValidationError):
        tariff.quote(start, start - timedelta(seconds=1))
    with pytest.raises(ValidationError):
        tariff.quote(start.replace(tzinfo=None), start)
