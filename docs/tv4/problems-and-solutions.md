# WBS 1.4 — Vấn đề, bài toán và giải pháp

Phạm vi bằng chứng: đọc mã repo nhóm tại `c1c9be4`, repo tham khảo `865b4a5`,
bảng WBS và các ảnh chia lượt. Tài liệu này chưa thay thế khảo sát trực tiếp bãi xe.

| Vấn đề được xác minh từ mã/tài liệu | Ảnh hưởng | Cách xử lý trong phần TV4 | Phần cần nhóm xác nhận |
|---|---|---|---|
| main.py gốc rỗng | Chưa có luồng chạy tích hợp | Controller camera, handler vào/ra, khởi chạy Qt | Tích hợp UI/OCR đầy đủ |
| UI/OCR gốc chưa hoàn thiện | Không thể chạy pipeline thật | Demo độc lập, lỗi khởi động rõ ràng | TV1/TV2 hoàn thiện module |
| closeEvent trong controller mẫu không phải cửa sổ Qt | Camera có thể chưa được release khi đóng | Main kế thừa QMainWindow; test sự kiện Qt thật | Chạy lại camera vật lý |
| Các nơi gọi chuyển ảnh dùng BGR/RGB không nhất quán | Có thể sai màu ảnh cắt biển | Một hợp đồng đầu vào BGR và QImage.copy | Kiểm tra trên video/model thật |
| Timer mẫu tiếp tục khi EOF | Lặp log, giữ nguồn không cần thiết | Dừng timer/release; khóa thao tác | Hành vi khi camera mất kết nối |
| Digit và box có thể không cùng biển khi nhiều box | Nguy cơ gắn nhầm xe | Chặn thao tác nếu không đúng một box | TV2 trả cặp biển số-box nếu hỗ trợ nhiều xe |
| Chưa có màn hình đặt/hủy và tra cứu theo WBS | Thiếu phần frontend TV4 | UserPortal và hợp đồng ParkingGateway | TV2 cung cấp adapter backend thật |
| Repo mẫu xóa ảnh khi xe ra | Không đủ lịch sử bền vững | UI lịch sử qua gateway; dữ liệu demo có phiên đã ra | CSDL và chính sách lưu ảnh của nhóm |
| UI mẫu nêu 3000/5000 nhưng không có quy tắc đầy đủ | Không xác định được kỳ vọng ca biên phí | Giá demo được ghi rõ; ca chính sách để blocked | TV3 chốt mốc giờ, làm tròn, qua ngày |

## Giả thuyết nghiệp vụ cần khảo sát

- Người dùng cần biết chỗ trống trước khi đặt.
- Hai yêu cầu cạnh tranh có thể chọn cùng một chỗ.
- Nhập/OCR sai biển số có thể gây gắn sai phiên gửi.
- Người vận hành cần tra cứu lịch sử và đối soát phí.

Chưa có số liệu hoặc phỏng vấn để khẳng định mức độ các vấn đề trên. TV4 bổ sung
người cung cấp thông tin, ngày khảo sát, kết quả và giới hạn mẫu; TV1 duyệt kết luận.
