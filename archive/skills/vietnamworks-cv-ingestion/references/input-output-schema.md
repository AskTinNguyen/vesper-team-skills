# Input/Output Schema — VietnamWorks CV Ingestion

## Input được hỗ trợ

- JSON array (`.json`)
- NDJSON (`.ndjson`), mỗi dòng là một object

## Input fields (linh hoạt alias)

Script hỗ trợ map nhiều tên field phổ biến về schema chuẩn:

- ID: `candidate_id`, `id`, `profile_id`
- Họ tên: `full_name`, `name`, `candidate_name`
- Vị trí/tiêu đề: `current_title`, `title`, `position`, `desired_position`
- Kinh nghiệm: `total_years_experience`, `experience_years`, `years_experience`
- Kỹ năng: `skills`, `skill_tags`, `primary_skills`
- Nguồn: `source`, `source_type`
- Consent: `consent_status`, `consent`, `privacy_consent`
- Link hồ sơ: `profile_url`, `url`
- Cập nhật gần nhất: `last_updated`, `updated_at`

## Output schema

```json
{
  "meta": {
    "processed_at": "ISO-8601",
    "input_count": 0,
    "accepted_count": 0,
    "excluded_count": 0,
    "filters": {
      "position": "string|null",
      "skills": ["skillA", "skillB"],
      "min_years": 0,
      "require_consent": true
    }
  },
  "records": [
    {
      "candidate_id": "string",
      "full_name": "string",
      "current_title": "string",
      "total_years_experience": 0,
      "skills": ["python", "sql"],
      "source": "user_export|ats_export|official_api|unknown",
      "consent_status": "granted|unknown|denied",
      "profile_url": "https://...",
      "last_updated": "ISO-8601|string|null"
    }
  ],
  "excluded": [
    {
      "candidate_id": "string|null",
      "reason": "string"
    }
  ]
}
```

## Lưu ý lọc

- `position`: match substring, không phân biệt hoa thường
- `skills`: yêu cầu ứng viên chứa đầy đủ tập kỹ năng nhập vào
- `min_years`: yêu cầu `total_years_experience >= min_years`
- `require_consent=true`: chỉ nhận hồ sơ có consent `granted/yes/true`
