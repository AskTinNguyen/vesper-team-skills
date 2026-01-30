# Detection Patterns

Heuristic grep patterns for finding code to delete. These are starting points — always verify before removing.

## 1. Unreachable Code

Code after return, throw, break, or continue that can never execute.

### JS/TS
```bash
grep -nP '^\s*(return|throw)\b' FILE | while read line; do
  lineno=$(echo "$line" | cut -d: -f1)
  next=$((lineno + 1))
  sed -n "${next}p" FILE | grep -qP '^\s*\S' && echo "Unreachable after line $lineno"
done
```

### Python
```bash
grep -nP '^\s*(return|raise|sys\.exit)\b' FILE | while read line; do
  lineno=$(echo "$line" | cut -d: -f1)
  indent=$(sed -n "${lineno}p" FILE | grep -oP '^\s*' | wc -c)
  next=$((lineno + 1))
  next_indent=$(sed -n "${next}p" FILE | grep -oP '^\s*' | wc -c)
  [ "$next_indent" -ge "$indent" ] 2>/dev/null && echo "Possibly unreachable after line $lineno"
done
```

### Go
```bash
grep -nP '^\s*(return|panic)\b' FILE
# Then manually check if statements follow at the same block level
```

## 2. Unused Imports / Variables / Functions

### JS/TS
```bash
# Unused imports — find imported names not referenced elsewhere
grep -oP 'import\s+\{([^}]+)\}' FILE | tr ',' '\n' | sed 's/[{ }]//g' | while read name; do
  count=$(grep -c "\b${name}\b" FILE)
  [ "$count" -le 1 ] && echo "Possibly unused import: $name"
done

# Unused exports — exported but never imported elsewhere
grep -rP "export\s+(function|const|class)\s+(\w+)" FILE | grep -oP '\w+$' | while read name; do
  count=$(grep -rl "\b${name}\b" --include='*.ts' --include='*.tsx' --include='*.js' . | wc -l)
  [ "$count" -le 1 ] && echo "Possibly unused export: $name"
done
```

### Python
```bash
# Unused imports
grep -P '^(from\s+\S+\s+)?import\s+' FILE | grep -oP '\b\w+$' | while read name; do
  count=$(grep -c "\b${name}\b" FILE)
  [ "$count" -le 1 ] && echo "Possibly unused import: $name"
done
```

### Go
```bash
# Go compiler catches unused imports/variables, but for quick scan:
grep -P '^\s+"[^"]+"\s*$' FILE | grep -oP '"([^"]+)"' | while read pkg; do
  short=$(basename "$pkg" | tr -d '"')
  count=$(grep -c "\b${short}\." FILE)
  [ "$count" -eq 0 ] && echo "Possibly unused import: $pkg"
done
```

## 3. Commented-Out Code Blocks

5+ consecutive comment lines containing code syntax (brackets, semicolons, keywords).

### General
```bash
awk '
  /^\s*(\/\/|#|--)\s*.*(function|class|if|for|return|import|const|let|var|def |;|\{|\})/ {
    if (NR == prev + 1) { run++ } else { run = 1 }
    prev = NR
    if (run >= 5) { print "Commented-out code block ending at line " NR }
  }
' FILE
```

### JS/TS — block comments
```bash
awk '
  /\/\*/ { in_comment = 1; start = NR }
  in_comment { lines++ }
  /\*\// { if (lines >= 5) print "Large block comment: lines " start "-" NR; in_comment = 0; lines = 0 }
' FILE
```

### Python — triple-quote blocks used as dead code
```bash
grep -nP '^\s*"""' FILE | paste - - | awk -F'[:\t]' '{ if ($3 - $1 >= 5) print "Possible dead code block: lines " $1 "-" $3 }'
```

## 4. Backward Compatibility Shims

Markers indicating code kept only for backward compatibility.

### General
```bash
grep -niP '(deprecated|legacy|compat|shim|backward.?compat|@deprecated|TODO.*remove|FIXME.*remove|hack|workaround|temporary)' FILE
```

### JS/TS
```bash
# JSDoc @deprecated tags
grep -nP '@deprecated' FILE

# Re-exports for backward compatibility
grep -nP 'export\s+\{.*\}\s+from' FILE | grep -iP '(compat|legacy|old)'
```

### Python
```bash
grep -nP '(warnings\.warn|DeprecationWarning|PendingDeprecationWarning)' FILE
```

## 5. Single-Implementation Interfaces

Interfaces or abstract classes with only one concrete implementor — abstraction without purpose.

### JS/TS
```bash
# Find interfaces, then check for implementations
grep -rP '(interface|abstract class)\s+(\w+)' --include='*.ts' --include='*.tsx' -l . | while read file; do
  grep -oP '(interface|abstract class)\s+(\w+)' "$file" | awk '{print $NF}' | while read name; do
    impls=$(grep -rlP "(implements|extends)\s+.*\b${name}\b" --include='*.ts' --include='*.tsx' . | wc -l)
    [ "$impls" -le 1 ] && echo "$file: $name has $impls implementor(s)"
  done
done
```

### Python
```bash
# Find ABCs with single subclass
grep -rP 'class\s+\w+\(.*ABC.*\)' --include='*.py' -l . | while read file; do
  grep -oP 'class\s+(\w+)\(.*ABC' "$file" | grep -oP '\w+(?=\()' | while read name; do
    subclasses=$(grep -rlP "class\s+\w+\(.*\b${name}\b" --include='*.py' . | wc -l)
    [ "$subclasses" -le 1 ] && echo "$file: ABC $name has $subclasses subclass(es)"
  done
done
```

### Go
```bash
# Find interfaces, count implementations
grep -rP 'type\s+(\w+)\s+interface' --include='*.go' . | grep -oP 'type\s+\K\w+' | while read name; do
  impls=$(grep -rlP "func\s+\([^)]+\)\s+${name}\b" --include='*.go' . | wc -l)
  [ "$impls" -le 1 ] && echo "Interface $name has $impls implementation(s)"
done
```

## 6. Functions Called Only Once

Functions called exactly once are inline candidates.

### JS/TS
```bash
grep -oP '(function\s+|const\s+)(\w+)\s*[=(]' FILE | grep -oP '\w+(?=\s*[=(])' | while read name; do
  count=$(grep -c "\b${name}\b" FILE)
  [ "$count" -le 2 ] && echo "Called at most once: $name (define + 1 call)"
done
```

### Python
```bash
grep -oP 'def\s+(\w+)' FILE | grep -oP '\w+$' | while read name; do
  count=$(grep -c "\b${name}\b" FILE)
  [ "$count" -le 2 ] && echo "Called at most once: $name"
done
```

### Go
```bash
grep -oP 'func\s+(\w+)' FILE | grep -oP '\w+$' | grep -v '^main$' | while read name; do
  count=$(grep -rc "\b${name}\b" --include='*.go' . | awk -F: '{s+=$NF} END {print s}')
  [ "$count" -le 2 ] && echo "Called at most once: $name"
done
```

---

**Note:** These patterns are heuristics. False positives are expected. Always verify context before deleting — a function may be called dynamically, an import may be used by a type checker, a shim may be load-bearing. Run tests after any deletion.
