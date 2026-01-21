# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of AI Academician seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email us at: **security@autospaien.com**
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 1 week
- **Resolution Timeline**: Depends on severity
  - Critical: 24-72 hours
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

### Disclosure Policy

- We follow responsible disclosure practices
- We will credit reporters (unless anonymity is requested)
- We ask that you give us reasonable time to address issues before public disclosure

## Security Best Practices

When using AI Academician:

1. **Never commit API keys** - Use environment variables
2. **Keep dependencies updated** - Run `pip install --upgrade`
3. **Use virtual environments** - Isolate project dependencies
4. **Review generated content** - AI outputs should be reviewed before publication

## Known Security Considerations

- This software makes API calls to external LLM providers
- Generated research papers should be reviewed for accuracy
- API keys should be stored securely using environment variables

Thank you for helping keep AI Academician secure!
