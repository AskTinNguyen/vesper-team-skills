---
name: vietnamworks-cv-ingestion
description: This skill should be used when working with VietnamWorks candidate profile data for internal HR workflows, including lawful data intake, normalization, compliance screening, and filtering by position, skills, and experience.
---

# VietnamWorks CV Ingestion

## Overview

Chuẩn hóa dữ liệu hồ sơ ứng viên từ VietnamWorks cho mục đích HR nội bộ theo hướng an toàn, tuân thủ ToS, và giới hạn dữ liệu được phép truy cập. Áp dụng bộ lọc theo vị trí, kỹ năng, kinh nghiệm và xuất ra dữ liệu chuẩn để dùng cho sàng lọc.

## Khi nào dùng skill

Kích hoạt skill khi có yêu cầu kiểu:
- "Chuẩn hóa hồ sơ ứng viên VietnamWorks"
- "Lọc CV theo vị trí/kỹ năng/số năm kinh nghiệm"
- "Nhập dữ liệu ứng viên từ file export hợp lệ"
- "Kiểm tra tuân thủ trước khi đưa CV vào pipeline nội bộ"

Không dùng skill này để:
- Vượt rào bảo vệ, bypass đăng nhập, hoặc thu thập dữ liệu không được cấp quyền
- Cào dữ liệu hàng loạt ngoài phạm vi tài khoản/nguồn được phép
- Thu thập hoặc phát tán dữ liệu cá nhân không cần thiết cho tuyển dụng

## Quy trình thực thi

### Bước 1: Xác minh quyền truy cập và tính hợp lệ nguồn dữ liệu

Thực hiện các kiểm tra bắt buộc trước khi xử lý:
1. Xác nhận dữ liệu đến từ nguồn hợp lệ: export chính chủ, ATS export, hoặc API chính thức có quyền.
2. Xác nhận mục đích xử lý là nội bộ tuyển dụng.
3. Xác nhận trạng thái consent hoặc quyền xử lý dữ liệu theo chính sách công ty.
4. Từ chối xử lý nếu nguồn không rõ ràng hoặc có dấu hiệu vi phạm ToS.

Chi tiết xem `references/compliance-and-safety.md`.

### Bước 2: Chuẩn hóa dữ liệu đầu vào

Dùng script:

```bash
python3 scripts/normalize_profiles.py \
  --input /absolute/path/to/raw_profiles.json \
  --output /absolute/path/to/normalized_profiles.json
```

Script sẽ:
- Đọc JSON array hoặc NDJSON
- Map field dị biệt sang schema chuẩn
- Loại bỏ trường PII không cần thiết (email, phone, address)
- Đánh dấu record bị loại và lý do loại

Schema I/O xem `references/input-output-schema.md`.

### Bước 3: Lọc theo nhu cầu tuyển dụng

Ví dụ lọc theo vị trí + kỹ năng + kinh nghiệm:

```bash
python3 scripts/normalize_profiles.py \
  --input /absolute/path/to/raw_profiles.json \
  --output /absolute/path/to/filtered_profiles.json \
  --position "backend" \
  --skills "python,sql" \
  --min-years 3
```

Nguyên tắc lọc:
- `--position`: so khớp chuỗi không phân biệt hoa thường trên tiêu đề hồ sơ
- `--skills`: yêu cầu ứng viên có đủ tất cả kỹ năng chỉ định
- `--min-years`: kinh nghiệm tối thiểu

### Bước 4: Kiểm soát an toàn và lưu vết

Bắt buộc thực hiện:
1. Chỉ lưu dữ liệu tối thiểu phục vụ tuyển dụng.
2. Không xuất dữ liệu nhạy cảm không cần thiết.
3. Ghi lại nguồn dữ liệu, thời điểm xử lý, tiêu chí lọc.
4. Thiết lập vòng đời dữ liệu (retention) theo chính sách nội bộ.

## Cấu hình an toàn khuyến nghị

- Chỉ xử lý file nằm trong workspace nội bộ tuyển dụng.
- Tách quyền đọc dữ liệu thô và quyền xuất dữ liệu đã chuẩn hóa.
- Dùng tài khoản dịch vụ riêng cho API chính thức (nếu có).
- Không commit dữ liệu ứng viên thô vào git repository.
- Mặc định bật chế độ yêu cầu consent (`--require-consent`).

## Resources

### scripts/
- `scripts/normalize_profiles.py`: Chuẩn hóa + lọc hồ sơ + kiểm tra compliance mức dữ liệu.

### references/
- `references/compliance-and-safety.md`: Checklist pháp lý/ToS và boundary vận hành.
- `references/input-output-schema.md`: Schema đầu vào/đầu ra và ví dụ dữ liệu.
