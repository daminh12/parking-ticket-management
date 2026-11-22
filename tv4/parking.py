"""Contract for TV2 integration and a nonpersistent demonstration adapter.

Demo rules are intentionally local to this module. They are not the team's
approved reservation, authorization or pricing rules.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
import re
from threading import RLock
from typing import Protocol
from uuid import uuid4


class ParkingError(Exception):
    """An actionable error safe to show in the frontend."""


class ValidationError(ParkingError):
    pass


class ConflictError(ParkingError):
    pass


class AccessError(ParkingError):
    pass


class SpaceState(str, Enum):
    FREE = "Trống"
    RESERVED = "Đã đặt"
    OCCUPIED = "Đang sử dụng"
    CLOSED = "Ngừng hoạt động"


@dataclass(frozen=True)
class Space:
    id: str
    zone: str
    vehicle_type: str
    state: SpaceState


@dataclass(frozen=True)
class Reservation:
    id: str
    owner_id: str
    space_id: str
    plate: str
    created_at: datetime
    status: str = "Đang giữ chỗ"


@dataclass(frozen=True)
class Visit:
    id: str
    owner_id: str
    plate: str
    space_id: str
    entered_at: datetime
    exited_at: datetime | None = None
    fee_vnd: int | None = None


class ParkingGateway(Protocol):
    """Bind this gateway to the authenticated identity on the service side.

    TV2's real adapter must enforce authorization and reservation conflicts in
    its backend/database, even when called outside this frontend.
    """
    def list_spaces(self) -> tuple[Space, ...]: ...
    def list_reservations(self) -> tuple[Reservation, ...]: ...
    def reserve(self, space_id: str, plate: str) -> Reservation: ...
    def cancel(self, reservation_id: str) -> None: ...
    def lookup(self, plate: str) -> tuple[Visit, ...]: ...


def normalize_plate(raw: str) -> str:
    """Normalize common civilian plate formats; not all Vietnamese plate types."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationError("Vui lòng nhập biển số.")
    if len(raw) > 32:
        raise ValidationError("Biển số nhập vào quá dài.")
    compact = re.sub(r"[\s.-]", "", raw).upper()
    if not 7 <= len(compact) <= 10 or not re.fullmatch(
        r"[0-9]{2}[A-Z][A-Z0-9]?[0-9]{4,6}", compact
    ):
        raise ValidationError("Biển số chưa hợp lệ. Ví dụ: 29A-12345 hoặc 36X1-4359.")
    return compact


class DemoFlatRate:
    """A 3000 VND per-visit illustration, not a day/night pricing policy."""
    def quote(self, entered_at: datetime, exited_at: datetime) -> int:
        if entered_at.utcoffset() is None or exited_at.utcoffset() is None:
            raise ValidationError("Thời gian phải có thông tin múi giờ.")
        if exited_at < entered_at:
            raise ValidationError("Giờ ra không được trước giờ vào.")
        return 3000


class DemoGateway:
    """In-memory, immediate reservations for one selected demo identity.

    Data disappears on restart. This adapter has no login, database, payment or
    cross-process locking. RLock only makes the local demonstration atomic.
    """
    def __init__(self, owner_id="TV4-DEMO"):
        self.owner_id = owner_id
        self._lock = RLock()
        self._spaces = {
            "A01": Space("A01", "A", "Ô tô", SpaceState.FREE),
            "A02": Space("A02", "A", "Ô tô", SpaceState.FREE),
            "A03": Space("A03", "A", "Ô tô", SpaceState.OCCUPIED),
            "A04": Space("A04", "A", "Ô tô", SpaceState.CLOSED),
            "B01": Space("B01", "B", "Xe máy", SpaceState.FREE),
            "B02": Space("B02", "B", "Xe máy", SpaceState.FREE),
        }
        self._reservations = {}
        self._visits = (
            Visit("DEMO-IN", owner_id, "29A11111", "A03",
                  datetime(2026, 11, 9, 2, 0, tzinfo=timezone.utc)),
            Visit("DEMO-OUT", owner_id, "36X14359", "B01",
                  datetime(2026, 11, 8, 2, 0, tzinfo=timezone.utc),
                  datetime(2026, 11, 8, 3, 0, tzinfo=timezone.utc), 3000),
        )

    def list_spaces(self):
        with self._lock:
            return tuple(self._spaces.values())

    def list_reservations(self):
        with self._lock:
            return tuple(record for record in self._reservations.values()
                         if record.owner_id == self.owner_id)

    def reserve(self, space_id, plate):
        plate = normalize_plate(plate)
        with self._lock:
            if space_id not in self._spaces:
                raise ValidationError("Vị trí đỗ không tồn tại.")
            space = self._spaces[space_id]
            if space.state != SpaceState.FREE:
                raise ConflictError("Chỗ vừa chọn không còn trống. Hãy tải lại danh sách.")
            if any(r.plate == plate and r.status == "Đang giữ chỗ"
                   for r in self._reservations.values()):
                raise ConflictError("Biển số này đang có một chỗ được giữ.")
            if any(v.plate == plate and v.exited_at is None for v in self._visits):
                raise ConflictError("Xe này đang có phiên gửi trong bãi.")
            record = Reservation(str(uuid4()), self.owner_id, space_id, plate,
                                 datetime.now(timezone.utc))
            self._reservations[record.id] = record
            self._spaces[space_id] = replace(space, state=SpaceState.RESERVED)
            return record

    def cancel(self, reservation_id):
        with self._lock:
            record = self._reservations.get(reservation_id)
            if record is None or record.owner_id != self.owner_id:
                raise AccessError("Không tìm thấy đặt chỗ thuộc tài khoản hiện tại.")
            space = self._spaces[record.space_id]
            if record.status != "Đang giữ chỗ" or space.state != SpaceState.RESERVED:
                raise ConflictError("Đặt chỗ không còn đủ điều kiện hủy.")
            self._reservations[record.id] = replace(record, status="Đã hủy")
            self._spaces[space.id] = replace(space, state=SpaceState.FREE)

    def lookup(self, plate):
        plate = normalize_plate(plate)
        with self._lock:
            return tuple(v for v in self._visits
                         if v.owner_id == self.owner_id and v.plate == plate)
