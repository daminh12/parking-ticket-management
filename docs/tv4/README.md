# Bàn giao phần TV4

Nguồn phân công: [WBS nhóm](https://docs.google.com/spreadsheets/d/1SJG7do2h3Qv6u7i_Jdirhp5a0XjguSp76I5kUp9aqKM/edit)
và ảnh lượt 8, 12, 16, 20. Nguồn mã tham khảo:
[vietanhlee/parking-ticket-management](https://github.com/vietanhlee/parking-ticket-management/tree/865b4a5da45802cf0e18d2c7ed224020c94b9000).

## Những gì có trong nhánh

| Phần việc | Tệp/đầu ra | Trạng thái có thể kiểm chứng |
|---|---|---|
| Các lượt main.py | `main.py`, `tv4/camera_demo.py` | Có controller và demo độc lập; chờ UI/OCR thật |
| WBS 1.4 | [Bảng vấn đề](problems-and-solutions.md) | Phân tích từ mã; khảo sát thực địa chưa có |
| WBS 2.4 | [Activity](activity.md), ba file `.puml` | Bản thiết kế để TV3/nhóm duyệt |
| WBS 2.9 | `tv4/portal.py`, ảnh trong `evidence/` | Prototype Qt chạy được |
| WBS 3.6 | Lọc chỗ, đặt/hủy và phản hồi lỗi | Frontend nối gateway demo; chờ backend TV2 |
| WBS 3.10 | Tra cứu, chuẩn hóa và trạng thái lỗi | Có kiểm thử với adapter demo |
| WBS 4.4 | `tests/`, [báo cáo](test-report.md), [CSV](manual-test-cases.csv) | Tự động/demo đã chạy; tích hợp thật còn pending |
| WBS 5.4 | [Chương 4](chapter4.md) | Bản thảo theo đúng kết quả hiện có |
| WBS 6.3 | [Kịch bản và biên bản](demo.md), evidence | Có chạy thử tự động/demo; chờ máy trình bày |

Không tự đánh dấu toàn bộ WBS hoàn thành khi khảo sát, quy tắc giá, backend và
model thật chưa được nhóm duyệt/chạy. Không sửa trạng thái Google Sheets trong lần bàn giao này.

## Chạy thử trên Windows

Tại thư mục repo, dùng PowerShell:

```powershell
py -3.12 -m venv .venv-tv4
.\.venv-tv4\Scripts\python.exe -m pip install -r requirements-tv4.txt
.\.venv-tv4\Scripts\python.exe main.py --demo
.\.venv-tv4\Scripts\python.exe -m tv4.portal
.\.venv-tv4\Scripts\python.exe -m pytest -q
```

Linux/macOS thay đường dẫn interpreter bằng `.venv-tv4/bin/python`.
Các demo không cần tải model, không ghi/xóa `image_data` và không lưu dữ liệu sau khi đóng.

## Giao ước tích hợp các lượt camera

TV1 cung cấp `Ui_MainWindow(window)` với các thuộc tính:
`label_main`, `label_plate`, `label_digits`, `label_in`, `label_time`,
`label_price`, `label_status`, `button_check_in`, `button_check_out`.

TV2 cung cấp `OcrPlate(path_model_detect_plate, path_model_ocr)` và
`set_data(imgage_input=frame_bgr)`, sau đó có `image_output`, `digit_out`, `box_xyxy`.
Giữ cách viết `imgage_input` để tương thích. Sentinel không nhận diện là `unknow`.
Controller hiện chỉ cho thao tác khi có đúng một box, tránh ghép sai digit-box.

TV3 trong bộ ảnh cung cấp `CheckAndSaveImg`: `check_exists`, `save_image`,
`delete_image`, `get_data -> (thời gian, ảnh BGR)`. Không thay đổi module đó trong nhánh.
Chế độ thật đặt `path_root` tuyệt đối theo thư mục repo.

Các lượt triển khai theo hành vi, không giữ số dòng cố định:

- Lượt 8: `convert_qimg` nhận BGR uint8, đổi RGB một lần, trả QImage sở hữu dữ liệu.
- Lượt 12: vào/ra kiểm tra trạng thái, chống lặp, đọc lại/xác minh kết quả lưu/xóa.
- Lượt 16: giữ ảnh gốc, nhận diện, kiểm tra box/crop, cập nhật UI, xóa trạng thái cũ khi lỗi.
- Lượt 20: closeEvent thuộc QMainWindow, dừng timer/release, import không mở GUI.

Mặc định hai model là `.pt`. Chế độ thật cần cài `requirements.txt` và PyQt5 rồi chạy
`python main.py --source test.MOV` hoặc `--source 0`. UI/OCR trên baseline chưa đầy đủ;
thông báo khởi động sẽ nêu nguyên nhân. QTimer chưa phải worker OCR; cần đo hiệu năng
máy nhóm trước khi quyết định QThread.

## Giao ước frontend WBS

`tv4.parking.ParkingGateway` là điểm nối với backend TV2. Khởi tạo:

```python
from tv4.portal import UserPortal
window = UserPortal(gateway=real_gateway, demo=False)
```

Adapter thật cung cấp `list_spaces`, `list_reservations`, `reserve`, `cancel`, `lookup`.
Đối tượng trả về theo các dataclass `Space`, `Reservation`, `Visit` trong `tv4.parking`.
Gateway phải được gắn với danh tính đã xác thực ở phía service, kiểm tra quyền và
xung đột trong backend/CSDL. Khóa UI hoặc RLock của demo không thay thế giao dịch CSDL.

Backend phản hồi lỗi nghiệp vụ bằng `ParkingError`/subclass với thông báo an toàn.
Lỗi hệ thống được log nội bộ; UI không hiển thị đường dẫn/chi tiết CSDL.
Nếu adapter gọi mạng mất thời gian, nhóm cần thêm worker để không chặn GUI thread.

## Quy tắc của demo, chưa phải quy tắc chính thức

- Giữ chỗ ngay, không có lịch đặt tương lai/thời hạn giữ.
- Một biển giữ một chỗ; không cho đặt khi xe đã có phiên đang mở.
- Hủy chỉ khi đặt đang giữ và chỗ còn trạng thái đã đặt; không giải phóng chỗ đang có xe.
- Chuẩn hóa biển phổ thông: trim/viết hoa/bỏ dấu cách, chấm, gạch. Regex không bao phủ
  mọi biển đặc biệt Việt Nam; TV1 duyệt phạm vi trước tích hợp.
- DemoFlatRate minh họa 3000 VND/lượt, có kiểm tra giờ ra không trước giờ vào.
  Chính sách ngày/đêm, làm tròn, qua ngày và thanh toán thật chưa được hiện thực.
- Ngày giờ portal hiển thị UTC+7; bản ghi dùng datetime có timezone.
- Mẫu tra cứu: `29A-11111` đang trong bãi, `36X1-4359` đã ra.
- Đây là dữ liệu trong bộ nhớ, không có đăng nhập, CSDL hoặc lưu lịch sử qua lần chạy.

## Trước khi đề nghị tích hợp vào main

- [ ] TV1/TV2 hoàn thiện UI/OCR và chạy model/video thật.
- [ ] TV2 nối adapter reservation/tra cứu có kiểm tra quyền và giao dịch CSDL.
- [ ] TV1/TV3 chốt quy tắc biển số, đặt/hủy và phí.
- [ ] Chạy CSV tích hợp và lưu bằng chứng trên máy nhóm.
- [ ] TV1 duyệt khảo sát, TV3 duyệt sơ đồ/prototype/Chương 4.
- [ ] Cả nhóm chạy thử trên máy trình bày và ghi biên bản.

Nhánh dành để review, không tự merge vào main.
