# WBS 6.3 — Kịch bản và biên bản chạy thử

## Chạy demo camera

1. Cài `requirements-tv4.txt` trong môi trường riêng.
2. Chạy `python main.py --demo`.
3. Kiểm tra banner minh họa và biển `29A - 12345`.
4. Xác nhận vào: ảnh/giờ vào xuất hiện, nút vào khóa, nút ra mở.
5. Xác nhận ra: bản ghi demo bị xóa, trạng thái cập nhật.
6. Nhấn X và mở lại: nguồn được giải phóng, dữ liệu demo không giữ qua lần chạy.

Chế độ này không dùng model, camera vật lý hoặc dữ liệu ảnh thực tế của người dùng.

## Chạy demo UI người dùng

1. Chạy `python -m tv4.portal`.
2. Xem sơ đồ chỗ và chữ trạng thái, lọc khu B rồi bỏ lọc.
3. Chọn A01, nhập `29A-12345`, xác nhận đặt.
4. Mở danh sách đặt, chọn bản ghi, xác nhận hủy; chỗ trở lại trống.
5. Tra `36X1-4359`: có phiên đã kết thúc và phí mẫu.
6. Tra `29A-11111`: có phiên đang gửi.
7. Tra biển không tồn tại và chuỗi rỗng: hai kết quả khác nhau; không giữ bảng cũ.

Không trình bày adapter trong bộ nhớ là CSDL hoặc xác thực thật.

## Bằng chứng chạy thử đã tạo

- Ngày chạy: 09/11/2026.
- Môi trường: Linux/Python 3.12, Qt offscreen.
- Script: `scripts/tv4_capture_demo.py --video`.
- Các assertion đã đạt: lọc còn hai chỗ khu B; đặt tạo một bản ghi; hủy đổi trạng thái;
  tra lịch sử có một phiên; ô rỗng xóa kết quả; camera vào/ra và release thành công.
- Ảnh: thư mục `evidence/`; video: `evidence/tv4-demo.webm`.
- Model OCR, backend thật và máy trình bày: chưa chạy, không thuộc bằng chứng này.

## Chạy thử cuối cùng cùng nhóm

| Mục | Người xác nhận / bằng chứng cần bổ sung |
|---|---|
| Commit tích hợp được chọn | Nhóm ghi SHA sau khi review |
| Máy và hệ điều hành trình bày | Nhóm ghi cấu hình |
| Model/camera thật | TV2 và TV4 chạy, quay màn hình |
| Backend/đăng nhập/CSDL | TV1–TV2 xác nhận |
| Giá và ca biên | TV3 xác nhận |
| Sơ đồ/prototype/Chương 4 | TV3 duyệt |
| Kịch bản chạy trực tiếp và dự phòng | Cả nhóm xác nhận |

## Dự phòng

- Giữ model, video nguồn và dependency local trước buổi trình bày.
- Chuẩn bị dữ liệu seed riêng, không thao tác trên dữ liệu thật của bãi xe.
- Thử chạy khi không có Internet nếu kiến trúc nhóm cho phép.
- Có video quay màn hình, ảnh, báo cáo PDF và hướng dẫn chạy.
- Nếu chiếu video dự phòng, nói rõ đó là bản ghi, không gọi là demo trực tiếp.
- Nhánh TV4 được review riêng; chỉ merge khi nhóm chủ động chấp thuận.
