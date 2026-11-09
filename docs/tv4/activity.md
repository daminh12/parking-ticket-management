# Bản nháp ba Activity Diagram

Nguồn Activity UML có swimlane để nhóm mở bằng PlantUML:
[đặt chỗ](reservation.puml), [xe vào](entry.puml), [xe ra](exit.puml).
Các flowchart dưới đây giúp xem nhanh luồng trên GitHub.

Các sơ đồ Mermaid dưới đây là bản mô tả luồng để nhóm duyệt. Muốn nộp Activity UML
chuẩn, chuyển thành UML với nút đầu/cuối, action, decision/merge, guard và swimlane.
Phân lane tối thiểu: Người dùng/Nhân viên — Giao diện — Service — CSDL.
Tác nhân và quyền chính thức phải theo ma trận TV1; quy tắc trạng thái theo WBS 2.5.

## A. Đặt chỗ

Giả định cần duyệt: người dùng đã đăng nhập; đặt theo khoảng thời gian chỉ khi SRS
yêu cầu. Backend TV2 chịu trách nhiệm chống xung đột bằng giao dịch/ràng buộc dữ liệu.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Người dùng mở tìm chỗ]
    B --> C[Nhập bộ lọc và thời gian nếu áp dụng]
    C --> D{Thông tin hợp lệ?}
    D -- Không --> E[Hiển thị lỗi nhập liệu]
    E --> C
    D -- Có --> F[Service tìm chỗ theo dữ liệu hiện tại]
    F --> G{Có chỗ phù hợp?}
    G -- Không --> H[Thông báo và cho đổi bộ lọc]
    H --> C
    G -- Có --> I[Người dùng chọn chỗ và xác nhận]
    I --> J[Backend kiểm tra quyền và trạng thái trong giao dịch]
    J --> K{Vẫn có thể đặt?}
    K -- Không --> L[Báo xung đột hoặc điều kiện không hợp lệ]
    L --> F
    K -- Có --> M[Lưu reservation và cập nhật trạng thái nguyên tử]
    M --> N{Commit thành công?}
    N -- Không --> O[Rollback và báo lỗi dịch vụ]
    O --> P([Kết thúc chưa đặt])
    N -- Có --> Q[Trả mã đặt và tải lại trạng thái]
    Q --> R([Kết thúc thành công])
```

Nhánh hủy bổ sung cho WBS 3.6: chọn đặt của mình → xác nhận hủy → backend kiểm tra
quyền/trạng thái/thời hạn → cập nhật trạng thái → phản hồi → tải lại danh sách.
Không giải phóng chỗ đang có xe chỉ vì người dùng nhấn hủy.

## B. Xe vào

Giả định cần duyệt: nhân viên vận hành xác nhận biển số; trường hợp không có reservation
có được tiếp nhận hay không phải theo quy tắc nhóm, không suy ra từ repo OCR.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Đọc camera hoặc nhận biển số theo SRS]
    B --> C{Có biển số hợp lệ?}
    C -- Không --> D[Báo không nhận diện hoặc yêu cầu xử lý theo SRS]
    D --> B
    C -- Có --> E[Nhân viên kiểm tra và xác nhận xe vào]
    E --> F[Service kiểm tra quyền và phiên gửi đang mở]
    F --> G{Xe đã trong bãi?}
    G -- Có --> H[Báo đã có phiên gửi; không tạo trùng]
    H --> Z([Kết thúc chưa tiếp nhận])
    G -- Không --> I[Kiểm tra reservation hoặc điều kiện tiếp nhận trực tiếp]
    I --> J{Có chỗ và đủ điều kiện?}
    J -- Không --> K[Báo hết chỗ hoặc sai điều kiện]
    K --> Z
    J -- Có --> L[Giao dịch tạo phiên gửi và chiếm chỗ]
    L --> M{Commit thành công?}
    M -- Không --> N[Rollback; không báo xe đã vào]
    N --> Z
    M -- Có --> O[Gắn thời gian và ảnh vào nếu có]
    O --> P[Hiển thị phiên gửi và trạng thái mới]
    P --> Q([Kết thúc thành công])
```

Đối với demo tham khảo chưa có CSDL/chỗ: rút gọn bước giao dịch thành kiểm tra thư mục
và lưu ảnh theo TV3, ghi rõ đây chỉ là mô phỏng. Cần chốt ảnh là bắt buộc hay tùy chọn;
nếu bắt buộc thì lỗi lưu ảnh phải được xử lý nhất quán với phiên gửi.

## C. Xe ra

Giả định cần duyệt: phí do TV3 cung cấp theo bảng quy tắc, thanh toán ở mức giả lập.
Nếu SRS không yêu cầu thanh toán thì bỏ action xác nhận thanh toán, không tự thêm hệ thống tiền thật.

```mermaid
flowchart TD
    A([Bắt đầu]) --> B[Nhận biển số và nhân viên xác nhận xe ra]
    B --> C{Biển số hợp lệ?}
    C -- Không --> D[Báo lỗi hoặc đọc lại]
    D --> B
    C -- Có --> E[Tra phiên gửi đang mở có quyền truy cập]
    E --> F{Tìm thấy phiên?}
    F -- Không --> G[Báo không có xe trong bãi]
    G --> Z([Kết thúc chưa cho ra])
    F -- Có --> H[Lấy giờ vào và giờ ra dự kiến]
    H --> I[Tính phí theo quy tắc đã duyệt]
    I --> J[Hiển thị thông tin và phí]
    J --> K{Xác nhận hoàn tất theo SRS?}
    K -- Không --> Z
    K -- Có --> L[Giao dịch kết thúc phiên, lưu phí, giải phóng chỗ]
    L --> M{Commit thành công?}
    M -- Không --> N[Rollback; giữ phiên mở và báo lỗi]
    N --> Z
    M -- Có --> O[Giữ lịch sử và tải lại trạng thái]
    O --> P([Kết thúc thành công])
```

Khác biệt cần nêu trong báo cáo: repo OCR tham khảo xóa thư mục ảnh khi xe ra, không có
giao dịch và lịch sử trong CSDL. Không vẽ các thành phần WBS rồi nói chúng đã được
hiện thực trong repo mẫu nếu chưa có code và kiểm thử tương ứng.
