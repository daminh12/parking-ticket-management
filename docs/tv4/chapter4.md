# Chương 4. Triển khai và kiểm thử phần TV4

## 4.1. Phạm vi và cách tổ chức

Phần TV4 được triển khai trên nhánh riêng từ baseline `c1c9be4`, gồm bộ điều phối
camera trong `main.py`, giao diện người dùng trong `tv4/portal.py`, hợp đồng tích hợp
`ParkingGateway`, adapter minh họa và bộ kiểm thử tự động. Các file UI/OCR/lưu ảnh của
thành viên khác được giữ nguyên.

Repo tham khảo là `vietanhlee/parking-ticket-management` tại `865b4a5`. Phần bổ sung
không sao chép toàn bộ ứng dụng tham khảo; giữ giao ước cần thiết để tích hợp các module.

## 4.2. Triển khai

### Điều phối camera

`Main` kế thừa `QMainWindow` để Qt gọi đúng sự kiện đóng. Model được khởi tạo một lần.
Mỗi timeout đọc frame, giữ ảnh gốc, gọi OCR, kiểm tra kết quả và cập nhật giao diện.
Ảnh BGR chuyển sang RGB tại một hàm duy nhất; `QImage.copy()` giữ dữ liệu độc lập.

Xác nhận vào kiểm tra bản ghi và đọc lại dữ liệu sau lưu. Xác nhận ra kiểm tra kết quả
xóa. Khi mất nhận diện hoặc lỗi, biển số/ảnh tạm bị xóa và nút thao tác bị khóa.
Khi hết nguồn hoặc đóng cửa sổ, timer dừng và capture được release.

API mẫu không trả liên kết rõ giữa từng box và biển số khi có nhiều xe. Controller
hiện chỉ cho thao tác khi có đúng một box. Đây là giới hạn có chủ đích để tránh gắn nhầm.

### Giao diện đặt/hủy chỗ

UserPortal có bộ lọc khu, loại xe và trạng thái; bảng chỗ; form biển số; danh sách đặt
của người dùng; xác nhận hủy. Trạng thái có chữ bên cạnh nên không phụ thuộc màu.
Sau thành công hoặc xung đột, UI tải lại dữ liệu. Lỗi dịch vụ không được hiển thị như
thao tác thành công. Khi tải lại thất bại, dữ liệu cũ bị xóa và nút đặt bị khóa.

Gateway tách UI với backend. Adapter demo dùng dữ liệu trong bộ nhớ và khóa trong
tiến trình để minh họa xung đột. Tích hợp thật cần TV2 kiểm tra quyền và giao dịch CSDL.

### Tra cứu và validation

Biển phổ thông được chuẩn hóa viết hoa và bỏ dấu phân cách đã quy định cho demo.
Chuỗi rỗng, quá dài, ký tự bất thường hoặc không đúng mẫu bị từ chối. Quy tắc này chưa
bao phủ mọi biển đặc biệt; cần TV1 duyệt trước tích hợp dữ liệu thật.

Tra cứu thể hiện phiên đang gửi, phiên đã ra, không có dữ liệu và lỗi dịch vụ riêng.
Khi truy vấn mới lỗi, kết quả cũ được xóa. Dữ liệu demo được giới hạn theo danh tính
minh họa; chưa có đăng nhập thật. Lịch sử demo tồn tại trong bộ nhớ, không bền vững.

### Phí

Adapter giá mẫu là 3000 VND/lượt và từ chối giờ ra trước giờ vào hoặc thời gian thiếu
timezone. Đây chỉ là quy tắc minh họa. Chính sách ngày/đêm, làm tròn, qua ngày và thanh
toán chưa được nhóm chốt nên chưa được báo là hoàn thành.

## 4.3. Minh chứng giao diện

Các ảnh/video trong `evidence/` được tạo từ ứng dụng chạy thật với dữ liệu mô phỏng.
Chúng chứng minh màn hình và luồng demo, không chứng minh model OCR hoặc CSDL thật.

- `portal-spaces.png`: tìm/lọc chỗ.
- `portal-reservation.png`: kết quả đặt chỗ.
- `portal-history.png`: tra cứu phiên đã kết thúc.
- `camera-demo.png`: bộ điều phối camera với ảnh/biển số tổng hợp.
- `tv4-demo.webm`: chạy thử các màn hình, đặt/hủy và tra cứu bằng dữ liệu demo.

## 4.4. Kiểm thử

Môi trường, số ca và lệnh đã chạy được ghi tại [báo cáo kiểm thử](test-report.md).
Test dùng Qt/OpenCV thật, kết hợp camera/OCR/storage mô phỏng và adapter demo.
Đã kiểm tra vòng đời camera, màu ảnh, trạng thái cũ, lỗi dịch vụ, đặt cạnh tranh,
hủy sai quyền/trạng thái, validation và tra cứu lịch sử mẫu.

Bảng `manual-test-cases.csv` là danh sách ca tích hợp để nhóm chạy với model/backend
và chính sách thật. Không chuyển các ca đó thành Pass chỉ từ kết quả demo.

## 4.5. Giới hạn và điều kiện nghiệm thu

- UI/OCR baseline của TV1/TV2 chưa đầy đủ, chưa chạy pipeline model thật.
- Chưa tích hợp backend tài khoản, reservation và CSDL nhóm.
- Khảo sát thực địa và các quy tắc chính thức vẫn cần người phụ trách duyệt.
- Chưa đo độ chính xác OCR, hiệu năng và hành vi camera vật lý trên máy trình bày.
- OCR và gateway hiện đồng bộ; cần worker nếu thời gian xử lý gây chặn GUI.

Bản thảo này phản ánh kết quả chuẩn bị trên nhánh TV4. Nhóm cần bổ sung bằng chứng
chạy tích hợp, ký duyệt và kết quả máy demo trước khi dùng làm báo cáo nghiệm thu cuối.
