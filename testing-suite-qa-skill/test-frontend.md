---
name: test-frontend
description: Frontend component testing for React, Vue, Svelte, and Angular with Vitest/Jest
argument-hint: "[target] [options]" e.g., "./src/components" or "Button --coverage"
---

# Test Frontend

Frontend component testing specialist for React, Vue, Svelte, and Angular applications. Generates comprehensive tests with proper coverage.

## When to Use

- Test React/Vue/Svelte/Angular components
- Setup frontend testing for new projects
- Add tests to existing components
- Verify component behavior and accessibility

## Usage

```bash
# Test all components
/test-frontend ./src/components

# Test specific component
/test-frontend ./src/components/Button

# Test with coverage report
/test-frontend ./src/components --coverage

# Test with watch mode (development)
/test-frontend ./src/components --watch

# Test matching a pattern
/test-frontend ./src/components -g "Button|Input"
```

## Auto-Detection

This command automatically detects:
- **Framework**: React, Vue, Svelte, Angular (from package.json)
- **Test Runner**: Vitest or Jest (from config files)
- **Testing Library**: React Testing Library, Vue Test Utils, etc.

## Test Generation

### Component Test Structure
```typescript
// Example: Button.test.tsx
describe('Button', () => {
  describe('Rendering', () => {
    it('renders children correctly')
    it('applies variant classes')
    it('handles disabled state')
  })

  describe('Interactions', () => {
    it('calls onClick when clicked')
    it('does not call onClick when disabled')
  })

  describe('Accessibility', () => {
    it('has correct ARIA labels')
    it('is keyboard navigable')
  })
})
```

### Coverage Requirements
- Props: 100% (all variants, sizes, states)
- Events: 100% (onClick, onChange, etc.)
- Conditions: 100% (if/else branches)
- Accessibility: 80% (ARIA, keyboard nav)

## Output

```
test-results/
├── component-test-results.json
├── coverage/
│   ├── lcov-report/
│   └── coverage-summary.json
└── failing-tests.log (if any)
```

## Best Practices

1. **Use data-testid** for stable selectors
2. **Test behavior, not implementation**
3. **Mock external dependencies**
4. **Test error states and loading states**
5. **Verify accessibility attributes**

## Integration

Called by `/test-orchestrator` when:
- Frontend files detected in changes
- Component tests requested
- Feature includes UI components
