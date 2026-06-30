# Windows Telegram MEDIA path pitfall

When delivering generated files from a Windows Hermes gateway session, use Windows-native absolute paths in `MEDIA:` tags:

```text
MEDIA:C:/Users/Admin/path/to/file.png
```

Do **not** use Git-Bash/MSYS paths such as:

```text
MEDIA:/c/Users/Admin/path/to/file.png
```

The terminal runs through Git-Bash, but the Telegram gateway's Python process resolves paths with Windows semantics. A `/c/Users/...` path is treated as `C:\c\Users\...`, so media extraction succeeds but Telegram delivery skips the file as missing. Gateway logs look like:

```text
[Telegram] Skipping missing image in media group: /c/Users/Admin/...
```

Recommended workflow after generating media in a bash command:

1. Copy or reference the file using a Windows-native path, e.g. `C:/Users/Admin/.hermes/cache/file.png`.
2. Verify from Python/Windows semantics if needed:

```bash
python - <<'PY'
import os
print(os.path.isfile('C:/Users/Admin/.hermes/cache/file.png'))
print(os.path.isfile('/c/Users/Admin/.hermes/cache/file.png'))  # False on native Windows Python
PY
```

3. Return `MEDIA:C:/Users/Admin/.hermes/cache/file.png` in the final response.

This applies to Telegram/media gateway delivery, not necessarily to shell commands. Shell commands on this host can still use `/c/Users/...` paths normally.
