# Compliance & Safety — VietnamWorks CV Ingestion

## Mục tiêu

Đảm bảo xử lý hồ sơ ứng viên đúng quyền truy cập, đúng mục đích tuyển dụng nội bộ, và giảm thiểu rủi ro pháp lý/riêng tư dữ liệu.

## Checklist trước khi ingest

1. Xác định nguồn dữ liệu:
   - `user_export`: file export từ tài khoản được cấp quyền
   - `ats_export`: xuất từ hệ thống ATS nội bộ
   - `official_api`: API chính thức với quyền hợp lệ
2. Xác định căn cứ xử lý dữ liệu:
   - Consent của ứng viên hoặc căn cứ hợp pháp tương đương theo chính sách công ty
3. Xác định phạm vi dữ liệu cần dùng:
   - Chỉ giữ field cần cho sàng lọc tuyển dụng
4. Xác định chính sách lưu trữ và xóa dữ liệu:
   - Có thời hạn retention rõ ràng

## Nguyên tắc bắt buộc

- Chỉ dùng dữ liệu có quyền truy cập hợp lệ.
- Không bypass cơ chế bảo vệ nền tảng.
- Không dùng bot scraping trái ToS.
- Không thu thập PII không cần thiết cho mục tiêu tuyển dụng.
- Không chia sẻ dữ liệu ứng viên ra ngoài phạm vi HR được ủy quyền.

## Dữ liệu nên loại bỏ khỏi output chuẩn hóa

- Email cá nhân
- Số điện thoại
- Địa chỉ chi tiết
- Thông tin định danh nhạy cảm khác

## Tình huống phải dừng xử lý

- Nguồn dữ liệu không xác minh được quyền sử dụng
- Yêu cầu thu thập dữ liệu ngoài phạm vi tuyển dụng
- Không có consent/căn cứ xử lý theo chính sách nội bộ
- Yêu cầu trích xuất hàng loạt nhằm mục đích không hợp lệ
