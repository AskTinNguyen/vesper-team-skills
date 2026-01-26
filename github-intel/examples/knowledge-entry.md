---
title: LRU Regex Cache
source: anthropics-claude-code
category: utilities
tags: [caching, regex, performance, python]
extracted: 2026-01-21
---

# LRU Regex Cache

## Overview

A Python decorator-based caching strategy for compiled regex patterns using `functools.lru_cache` to prevent expensive recompilation. This pattern is widely applicable wherever regex patterns are used repeatedly.

## Problem

Regex compilation is computationally expensive. When the same patterns are used repeatedly in loops, hot paths, or rule evaluation engines, recompiling them wastes CPU cycles and increases latency.

Common scenarios:
- Log parsing with repeated patterns
- Input validation rules
- Text transformation pipelines
- Configuration-driven pattern matching

## Solution

### Core Concept

Use Python's built-in LRU (Least Recently Used) cache to memoize compiled regex Pattern objects. The cache is bounded to prevent memory bloat.

### Implementation

```python
from functools import lru_cache
import re
from typing import Pattern

@lru_cache(maxsize=128)
def compile_regex(pattern: str, flags: int = re.IGNORECASE) -> Pattern:
    """
    Compile and cache a regex pattern.

    Args:
        pattern: Regular expression string
        flags: Regex flags (default: case-insensitive)

    Returns:
        Compiled Pattern object (cached on subsequent calls)

    Note:
        maxsize=128 limits memory usage while covering most use cases.
        Adjust based on expected pattern diversity.
    """
    return re.compile(pattern, flags)
```

### Usage

```python
# First call: compiles and caches
pattern = compile_regex(r"user-\d+")
match = pattern.match("user-123")

# Subsequent calls: instant cache hit
pattern = compile_regex(r"user-\d+")  # No recompilation
match = pattern.match("user-456")

# Different pattern: new compilation + cache
email_pattern = compile_regex(r"[\w.-]+@[\w.-]+\.\w+")
```

### With Multiple Flags

```python
@lru_cache(maxsize=128)
def compile_regex_with_flags(pattern: str, multiline: bool = False) -> Pattern:
    flags = re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    return re.compile(pattern, flags)

# Cache keys include all arguments
pattern1 = compile_regex_with_flags(r"^start", multiline=True)
pattern2 = compile_regex_with_flags(r"^start", multiline=False)  # Different cache entry
```

## Variations

### Unbounded Cache

For applications with limited pattern diversity:

```python
@lru_cache(maxsize=None)  # Unlimited cache
def compile_regex_unbounded(pattern: str) -> Pattern:
    return re.compile(pattern)
```

### Thread-Local Cache

For thread-specific caching (useful when patterns vary by thread):

```python
import threading

_local = threading.local()

def get_thread_cache():
    if not hasattr(_local, 'regex_cache'):
        _local.regex_cache = {}
    return _local.regex_cache

def compile_regex_threaded(pattern: str) -> Pattern:
    cache = get_thread_cache()
    if pattern not in cache:
        cache[pattern] = re.compile(pattern)
    return cache[pattern]
```

### Cache Statistics

```python
# Check cache performance
info = compile_regex.cache_info()
print(f"Hits: {info.hits}, Misses: {info.misses}, Size: {info.currsize}")

# Clear cache if needed
compile_regex.cache_clear()
```

## Trade-offs

**Pros:**
- Zero-config performance improvement
- Bounded memory with maxsize
- Thread-safe in Python 3.2+
- No external dependencies
- Transparent to callers

**Cons:**
- Cache misses on new patterns (first call still slow)
- Memory overhead for cache storage
- Not suitable for one-time patterns
- LRU eviction may remove frequently-used patterns if maxsize too small

## When to Use

**Good fit:**
- Rule engines with repeated patterns
- Log parsers with known pattern sets
- Validation libraries
- Template systems

**Avoid when:**
- Every pattern is unique (no reuse)
- Memory is extremely constrained
- Patterns change frequently

## Related Patterns

- **Memoization** - General caching pattern this builds on
- **Object Pool** - Alternative for expensive object creation
- **Flyweight** - Sharing common objects

## References

- Source: `anthropics-claude-code/plugins/hookify/core/rule_engine.py:15`
- Python docs: [functools.lru_cache](https://docs.python.org/3/library/functools.html#functools.lru_cache)
