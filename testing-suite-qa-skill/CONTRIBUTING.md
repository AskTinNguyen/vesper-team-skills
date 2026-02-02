# Contributing to Testing Suite

Thank you for your interest in contributing to the Testing Suite for Claude Code! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Workflow](#development-workflow)
- [Command File Structure](#command-file-structure)
- [Testing Your Changes](#testing-your-changes)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Accept responsibility for mistakes

## Getting Started

### Prerequisites

- Claude Code CLI installed
- Git installed
- Familiarity with Markdown
- Understanding of testing concepts

### Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/vesper-team-skills.git
cd vesper-team-skills

# Add upstream remote
git remote add upstream https://github.com/AskTinNguyen/vesper-team-skills.git
```

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:

1. Check if the bug has already been reported in [Issues](https://github.com/AskTinNguyen/vesper-team-skills/issues)
2. Try to reproduce the issue with the latest version
3. Collect information about the bug

When creating a bug report, include:

- **Command used**: Which testing command failed
- **Input provided**: What arguments or context you gave
- **Expected behavior**: What should have happened
- **Actual behavior**: What actually happened
- **Environment**: OS, Claude Code version, project type
- **Logs/Errors**: Any error messages or output

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- Use a clear, descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the enhancement
- Explain why this enhancement would be useful

### Adding New Test Types

Want to add support for a new testing framework or language?

1. Create a new command file in `commands/workflows/`
2. Follow the [Command File Structure](#command-file-structure)
3. Include auto-detection logic
4. Add example test patterns
5. Update the main README

### Improving Documentation

Documentation improvements are always welcome:

- Fix typos or unclear explanations
- Add more examples
- Improve code comments
- Translate to other languages

## Development Workflow

### 1. Create a Branch

```bash
# Pull latest changes from upstream
git checkout main
git pull upstream main

# Create your feature branch
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Edit the relevant command files. Test your changes locally.

### 3. Commit Changes

```bash
git add .
git commit -m "type: description

Detailed explanation of what and why"
```

Commit message types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test-related changes
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub.

## Command File Structure

Every command file must follow this structure:

```markdown
---
name: command-name
description: Brief description (max 100 chars)
argument-hint: "[expected arguments]"
---

# Command Title

Brief introduction.

## When to Use

List scenarios where this command is appropriate.

## Usage

```bash
/command-name [arguments]
```

## Auto-Detection

Describe what the command auto-detects.

## Test Patterns

Show example test structures.

## Output

Describe output files and locations.

## Best Practices

List do's and don'ts.

## Integration

Explain how this integrates with other commands.
```

### Required Sections

1. **YAML Frontmatter** (mandatory)
   - `name`: Lowercase, hyphenated
   - `description`: Max 100 characters
   - `argument-hint`: Show expected arguments

2. **Title and Introduction**
   - Clear command name
   - One-paragraph description

3. **When to Use**
   - Bullet list of scenarios

4. **Usage Examples**
   - Common use cases
   - All available options

5. **Output**
   - File locations
   - Format descriptions

6. **Integration**
   - How it fits with other commands

## Testing Your Changes

### Test Locally

```bash
# Copy to your Claude Code commands
cp commands/workflows/my-command.md ~/.claude/commands/

# Test the command in Claude Code
/claude
> /my-command [test arguments]
```

### Checklist

Before submitting:

- [ ] Command has YAML frontmatter
- [ ] All sections are complete
- [ ] Examples are tested and working
- [ ] No typos or grammar errors
- [ ] Follows style guidelines
- [ ] Integration with other commands documented

## Submitting Changes

### Pull Request Process

1. Update the CHANGELOG.md with your changes
2. Ensure your PR description clearly describes the problem and solution
3. Include the relevant issue number if applicable
4. Wait for code review
5. Address any feedback

### PR Title Format

```
type(scope): description

Examples:
- feat(test-e2e): add mobile viewport support
- fix(test-backend): resolve database cleanup issue
- docs: improve command examples
```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Refactoring

## Testing
How did you test these changes?

## Checklist
- [ ] Command tested locally
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] No breaking changes (or documented)
```

## Style Guidelines

### Writing Style

- Be concise but clear
- Use active voice
- Include code examples
- Use consistent terminology

### Formatting

- Use Markdown for all documentation
- Code blocks should specify language
- Use headers hierarchically (H1 → H2 → H3)
- Limit line length to 100 characters when possible

### Command Naming

- Use lowercase with hyphens: `test-frontend`, not `TestFrontend`
- Be descriptive but concise
- Follow existing naming patterns

### Examples

Always include practical examples:

```markdown
## Usage

### Test All Components
```bash
/test-frontend ./src/components
```

### Test with Coverage
```bash
/test-frontend ./src/components --coverage
```
```

## Questions?

- Join our [GitHub Discussions](https://github.com/AskTinNguyen/vesper-team-skills/discussions)
- Open an [Issue](https://github.com/AskTinNguyen/vesper-team-skills/issues)
- Contact maintainers

## Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Added to the contributors graph

Thank you for contributing! 🎉
