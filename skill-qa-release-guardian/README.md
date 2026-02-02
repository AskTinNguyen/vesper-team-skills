# QA Release Guardian Skill

> Claude Code SKILL for automated release QA - UI exploratory testing, regression verification, PR-aware retesting, and structured bug reporting.

## Tính năng

- **UI Exploratory Testing** - Tự động khám phá và test tất cả screens, buttons, forms
- **Issue-Based Regression** - Verify các bug đã fixed không bị regression  
- **PR-Aware Retesting** - Focus test vào areas bị ảnh hưởng bởi PR mới merge
- **Structured Bug Reporting** - Báo cáo bug có cấu trúc, đủ evidence cho dev fix

## Cài đặt

### Clone repo về máy:

```bash
git clone <repo-url>
cd qa-release-guardian
```

### Copy skill vào project của bạn:

```bash
# Copy cả folder skills vào .claude/ trong project của bạn
cp -r skills/qa-release-guardian /path/to/your/project/.claude/skills/
```

Hoặc copy vào global skills:

```bash
# Copy vào global Claude skills
mkdir -p ~/.claude/skills
cp -r skills/qa-release-guardian ~/.claude/skills/
```

## Sử dụng

### Cách 1: Dùng trong Claude Code

Mở project trong Claude Code và chạy:

```
qa-release-guardian --base_url=http://localhost:3000
```

### Cách 2: Với config file

Tạo file `.qa-guardian.yml` trong project root:

```yaml
base_url: https://staging.app.com
auth:
  type: cookie
  file: ./auth-state.json

github:
  repo: your-org/your-repo
  since: last_7_days

scope:
  mode: full
  max_depth: 3
  exclude_routes:
    - /admin/**
    - /internal/**

safety:
  allow_write_actions: false

reporting:
  output_dir: ./qa-reports
  screenshot_on_error: true
```

## Quick Start Commands

```bash
# Basic smoke test
qa-release-guardian --base_url=http://localhost:3000

# Full test trên staging
qa-release-guardian --base_url=https://staging.app.com --scope=full

# Chỉ test regression (nhanh hơn)
qa-release-guardian --base_url=https://app.com --scope=regression_only --since=last_7_days

# Với authentication
qa-release-guardian --base_url=https://app.com --auth=cookie --auth_file=./auth.json
```

## Files trong Skill

```
skills/qa-release-guardian/
├── SKILL.md              # Chi tiết implementation
├── config-schema.json    # JSON schema cho config validation
└── example-config.yml    # Config mẫu để tham khảo
```

## Yêu cầu

- Claude Code (có support skills)
- GitHub CLI (`gh`) đã authenticated (cho GitHub integration)
- Agent Browser skill (thường có sẵn trong Claude Code)

## License

Internal tool - Share freely for QA teams.

---

Made with ❤️ for QA automation
