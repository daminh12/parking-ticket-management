# 🚗 Parking Ticket Management - Hệ Thống Quản Lý Bãi Xe Thông Minh

Hệ thống quản lý vé xe thông minh ứng dụng thị giác máy tính (AI / Computer Vision) để tự động phát hiện phương tiện, nhận diện và đọc biển số xe (OCR), đối soát xe ra/vào bãi và lưu trữ lịch sử bằng hình ảnh.

---

## 📌 Tính năng chính

- **Nhận diện biển số thời gian thực (Real-time License Plate Detection & OCR):** Tự động phát hiện vị trí biển số và bóc tách các ký tự chữ số bằng mô hình YOLO & ONNX.
- **Xác nhận xe vào bãi (Check-in):** Lưu trữ toàn cảnh ảnh xe vào thư mục biển số tương ứng kèm mốc thời gian (ngày, giờ, phút, giây).
- **Kiểm tra trạng thái & xe trong bãi:** Tự động tra cứu lịch sử, hiển thị thời gian vào bãi và ảnh chụp đối chứng của xe.
- **Xác nhận xe ra bãi (Check-out):** Tính toán và đối soát vé xe, tự động dọn dẹp dữ liệu lưu trữ khi xe rời bãi.

---

## 📂 Cấu trúc thư mục

```text
parking-ticket-management/
├── model/                     # Chứa các model ONNX và YOLO (Plate & OCR)
│   ├── best_plate_int8.onnx   # Model phát hiện vùng biển số (đã tối ưu int8)
│   ├── best_ocr_int8.onnx     # Model OCR đọc ký tự biển số (đã tối ưu int8)
├── image_data/                # Thư mục tự động tạo để lưu ảnh xe theo biển số
├── display_github/            # Ảnh minh họa và tài liệu dự án
├── main.py                    # Khởi chạy luồng chính và kết nối giao diện
├── main_ui.py                 # Thiết kế giao diện PyQt5 hiện đại
├── OcrPlate.py                # Module AI xử lý nhận diện biển số & OCR
├── check_and_save_img.py      # Module xử lý lưu trữ, xóa và đọc ảnh dữ liệu xe
├── test.MOV                   # Video mẫu để kiểm thử khi không có camera trực tiếp
├── requirements.txt           # Danh sách các thư viện cần thiết
└── README.md                  # Tài liệu hướng dẫn sử dụng
```

---

## ⚙️ Hướng dẫn cài đặt và sử dụng

### 1. Yêu cầu hệ thống
- **Python**: Phiên bản khuyến nghị từ `3.9` đến `3.12`.
- Hệ điều hành: Windows, macOS hoặc Linux.

---

### 2. Các bước cài đặt chi tiết

#### **Bước 1: Clone dự án về máy**
Mở terminal (PowerShell, Command Prompt hoặc Git Bash) và chạy lệnh:
```bash
git clone https://github.com/daminh12/parking-ticket-management.git
cd parking-ticket-management
```

#### **Bước 2: Tạo và kích hoạt môi trường ảo (Khuyến nghị)**
Tạo môi trường ảo giúp tránh xung đột phiên bản với các gói thư viện khác trên máy:

- **Trên Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(Nếu gặp lỗi PowerShell chặn script, chạy lệnh: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` rồi kích hoạt lại)*

- **Trên Windows (Command Prompt - cmd):**
  ```cmd
  python -m venv .venv
  .\.venv\Scripts\activate.bat
  ```

- **Trên macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

#### **Bước 3: Nâng cấp pip và cài đặt thư viện cần thiết**
Chạy lệnh sau để cài đặt đầy đủ tất cả các gói phụ thuộc:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Danh sách các thư viện chính bao gồm:
- `PyQt5`: Xây dựng giao diện ứng dụng.
- `opencv-python`: Đọc và xử lý luồng video/ảnh camera.
- `ultralytics` & `torch`: Chạy mô hình phát hiện đối tượng YOLO.
- `onnxruntime`: Tối ưu hóa suy luận (inference) mô hình ONNX nhanh trên CPU.
- `numpy`: Xử lý mảng dữ liệu ảnh và tọa độ bounding box.

---

### 3. Khởi chạy ứng dụng

Chạy lệnh sau tại thư mục gốc của dự án:
```bash
python main.py
```

---

## 💡 Lưu ý quan trọng để chạy trơn tru không lỗi

1. **Thứ tự import trên Windows (Tránh lỗi Crash ngầm / Silent Crash):**
   - Trên hệ điều hành Windows, thư viện PyTorch / ONNX Runtime (`torch`, `ultralytics`) **bắt buộc phải được import trước** `PyQt5` và `cv2` trong file `main.py` để tránh xung đột thư viện động (`c10.dll` / `libiomp5md.dll`).
   - Giữ nguyên cấu trúc import ở đầu file `main.py`:
     ```python
     import torch
     from ultralytics import YOLO
     from main_ui import Ui_MainWindow
     from PyQt5.QtWidgets import QMainWindow, QApplication
     ```

2. **Chuyển đổi nguồn Camera:**
   - Mặc định chương trình đang chạy thử nghiệm bằng video mẫu `test.MOV`.
   - Để chuyển sang sử dụng **Webcam máy tính** hoặc **Camera IP / USB trực tiếp**, mở file `main.py` và sửa dòng 17:
     ```python
     # Chạy bằng video có sẵn:
     self.cap = cv2.VideoCapture(r'test.MOV')

     # Đổi sang Webcam máy tính (thường là camera số 0):
     self.cap = cv2.VideoCapture(0)
     ```

```

---

## 💡 Lưu ý quan trọng để chạy trơn tru không lỗi

1. **Thứ tự import trên Windows (Tránh lỗi Crash ngầm / Silent Crash):**
   - Trên hệ điều hành Windows, thư viện PyTorch / ONNX Runtime (`torch`, `ultralytics`) **bắt buộc phải được import trước** `PyQt5` và `cv2` trong file `main.py` để tránh xung đột thư viện động (`c10.dll` / `libiomp5md.dll`).
   - Giữ nguyên cấu trúc import ở đầu file `main.py`:
     ```python
     import torch
     from ultralytics import YOLO
     from main_ui import Ui_MainWindow
     from PyQt5.QtWidgets import QMainWindow, QApplication
     ```

2. **Chuyển đổi nguồn Camera:**
   - Mặc định chương trình đang chạy thử nghiệm bằng video mẫu `test.MOV`.
   - Để chuyển sang sử dụng **Webcam máy tính** hoặc **Camera IP / USB trực tiếp**, mở file `main.py` và sửa dòng 17:
     ```python
     # Chạy bằng video có sẵn:
     self.cap = cv2.VideoCapture(r'test.MOV')

     # Đổi sang Webcam máy tính (thường là camera số 0):
     self.cap = cv2.VideoCapture(0)
     ```