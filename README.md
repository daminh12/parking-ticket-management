# Parking Ticket Management

Đồ án chuyên đề Hệ thống giao thông thông minh: quản lý vé xe bằng nhận diện biển số.

## Cấu trúc dự án
- `display_github/` – ảnh minh họa dự án
- `image_data/` – ảnh xe được lưu
- `model/` – các model nhận diện
- `main_ui.py` – giao diện chương trình
- `OcrPlate.py` – nhận diện biển số
- `check_and_save_img.py` – lưu và kiểm tra ảnh xe
- `main.py` – điều khiển chương trình chính
- `test.MOV` – video kiểm thử

## Phần TV4 trên nhánh riêng

TV4 bổ sung bộ điều phối camera trong `main.py`, giao diện đặt/hủy chỗ và tra cứu
trong `tv4/`, kiểm thử trong `tests/` và tài liệu bàn giao trong `docs/tv4/`.

### Chạy demo TV4 ngay

```bash
python -m venv .venv-tv4
# Windows: .venv-tv4\Scripts\python.exe
# Linux/macOS: .venv-tv4/bin/python
python -m pip install -r requirements-tv4.txt
python main.py --demo
python -m tv4.portal
```

Chạy các lệnh `python` bằng interpreter của môi trường vừa tạo (hoặc kích hoạt
môi trường trước). Hai demo dùng dữ liệu mô phỏng và không lưu sau khi đóng.
Demo camera không sử dụng model OCR thật. Demo đặt chỗ chưa kết nối tài khoản,
CSDL hoặc chính sách giá chính thức của nhóm.

### Tích hợp camera/OCR thật

```bash
python -m pip install -r requirements.txt
python -m pip install PyQt5==5.15.11
python main.py --source test.MOV
# Camera vật lý:
python main.py --source 0
```

Chế độ này cần UI của TV1 và `OcrPlate.py` của TV2 hoàn thiện. Baseline hiện tại
chưa đủ hai module đó; TV4 giữ nguyên các file của thành viên khác. Controller
mặc định dùng `model/best_plate.pt` và `model/best_ocr.pt`, tải một lần khi mở.

### Kiểm thử

```bash
python -m pytest -q
# Linux không có màn hình:
QT_QPA_PLATFORM=offscreen python -m pytest -q
```

Không cài đồng thời `opencv-python` và `opencv-python-headless` trong cùng môi trường.

Xem [hướng dẫn và phạm vi bàn giao TV4](docs/tv4/README.md),
[báo cáo kiểm thử](docs/tv4/test-report.md),
[ba luồng Activity](docs/tv4/activity.md) và
[bảng test tích hợp cần nhóm chạy](docs/tv4/manual-test-cases.csv).

## Nguồn tham khảo

- https://github.com/vietanhlee/parking-ticket-management — giao ước camera/OCR/lưu ảnh.
- Bảng WBS của nhóm được dẫn trong tài liệu TV4; mã bổ sung và dữ liệu minh họa được
  phân biệt với chức năng gốc và các module còn chờ tích hợp.
