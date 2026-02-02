---
name: test-e2e
description: End-to-end testing with Playwright for web applications
argument-hint: "[target] [options]" e.g., "./e2e" or "./e2e/login.spec.ts --project=chromium"
---

# Test E2E

End-to-end testing with Playwright. Tests complete user flows across browsers with visual regression support.

## When to Use

- Test critical user flows
- Cross-browser testing
- Visual regression testing
- Test before production release

## Usage

```bash
# Run all E2E tests
/test-e2e ./e2e

# Run specific test file
/test-e2e ./e2e/login.spec.ts

# Run specific browser
/test-e2e ./e2e --project=chromium
/test-e2e ./e2e --project=firefox
/test-e2e ./e2e --project=webkit

# Debug mode (headed with UI)
/test-e2e ./e2e --ui

# Update visual snapshots
/test-e2e ./e2e --update-snapshots

# Run with trace (for debugging failures)
/test-e2e ./e2e --trace on
```

## Page Object Model (POM)

Generated tests use POM pattern:

```typescript
// pages/LoginPage.ts
class LoginPage extends BasePage {
  readonly emailInput = this.page.locator('[data-testid="email"]')
  readonly passwordInput = this.page.locator('[data-testid="password"]')
  readonly loginButton = this.page.locator('[data-testid="login-button"]')

  async login(email: string, password: string) {
    await this.fill(this.emailInput, email)
    await this.fill(this.passwordInput, password)
    await this.click(this.loginButton)
  }
}
```

## Test Patterns

### Critical User Flows
```typescript
test('complete purchase flow', async () => {
  // Login → Browse → Add to cart → Checkout → Verify
})
```

### Visual Regression
```typescript
test('homepage matches snapshot', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveScreenshot('homepage.png')
})
```

### Cross-Browser
- Chromium (Chrome/Edge)
- Firefox
- WebKit (Safari)
- Mobile viewports

## Configuration

Auto-generates `playwright.config.ts` with:
- Parallel execution
- Retry logic (2x in CI)
- Screenshot on failure
- Video on failure
- Trace for debugging

## Output

```
test-results/
├── playwright-report/
│   └── index.html
├── blob-report/
├── screenshots/
│   └── *.png (on failure)
├── videos/
│   └── *.webm (on failure)
└── traces/
    └── *.zip (for debugging)
```

## Best Practices

1. **Use resilient selectors** (data-testid > text > CSS)
2. **Avoid hardcoded waits** (use auto-waiting)
3. **Test realistic user flows**
4. **Clean up test data after**
5. **Run in parallel**

## Integration

Called by `/test-orchestrator` when:
- Critical flows need verification
- Cross-browser testing required
- Pre-release validation
