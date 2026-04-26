# Security Policy

## Table of Contents

- [Supported Versions](#-supported-versions)
- [Reporting a Vulnerability](#-reporting-a-vulnerability)
- [Response Timeline](#-response-timeline)
- [Disclosure Policy](#-disclosure-policy)
- [Security Best Practices for Deployers](#-security-best-practices-for-deployers)
  - [Django Settings](#django-settings)
  - [Secret Key](#secret-key)
  - [Database](#database)
  - [Authentication](#authentication)
  - [HTTPS & Headers](#https--headers)
  - [File Uploads](#file-uploads)
  - [Environment Variables](#environment-variables)
- [Known Security Considerations](#-known-security-considerations)
- [Security Features Built Into This Project](#-security-features-built-into-this-project)
- [Hall of Fame](#-hall-of-fame)
- [Contact](#-contact)

---

## ✅ Supported Versions

We actively maintain and release security patches for the following versions:

| Version | Supported | Notes |
|---------|-----------|-------|
| `v2.0.0` (latest) | ✅ Active support | Current stable release |
| `v1.x.x` | ⚠️ Critical fixes only | Upgrade to v2 recommended |
| `< v1.0` | ❌ Not supported | No security patches |

> **Recommendation:** Always run the latest release. Older versions may contain
> unpatched vulnerabilities. Check the
> [Releases page](https://github.com/Ansarimajid/College-ERP/releases) for
> the most current version.

---

## 🔒 Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub Issues,
Pull Requests, or Discussions.** Public disclosure before a fix is available
puts all users of this software at risk.

### How to report

Send a detailed email to:

**📧 ansmajidali@gmail.com**

Use the subject line:
```
[SECURITY] College-ERP — <brief description>
```

### What to include in your report

Please provide as much of the following as possible:

```
1. Vulnerability type
   (e.g. SQL Injection, XSS, CSRF bypass, IDOR, broken auth, etc.)

2. Affected component
   (e.g. student login view, attendance API, file upload handler)

3. Affected version(s)
   (e.g. v2.0.0, or commit hash if running from source)

4. Steps to reproduce
   Provide clear, numbered steps that allow us to reproduce the issue.
   Include any payloads, request/response examples, or screenshots.

5. Proof of concept (PoC)
   A working example demonstrating the vulnerability, if possible.
   Code snippets, curl commands, or Burp Suite exports are all helpful.

6. Impact assessment
   What can an attacker achieve by exploiting this?
   (e.g. read other students' grades, escalate to admin, execute code)

7. Suggested fix (optional)
   If you have a recommendation for how to fix it, include it here.

8. Your name / handle (optional)
   For credit in the Hall of Fame and release notes, if you wish.
```

### Encryption (optional)

If your report contains highly sensitive details, you may request our PGP
public key before sending by emailing ansmajidali@gmail.com with the subject
`[PGP KEY REQUEST]`.

---

## ⏱ Response Timeline

We take security reports seriously and commit to the following timeline:

| Milestone | Target time |
|-----------|-------------|
| Initial acknowledgement | Within **48 hours** of receiving your report |
| Vulnerability confirmed / triage complete | Within **5 business days** |
| Fix developed and tested | Within **14 days** for critical/high issues |
| Patched release published | Within **21 days** for critical/high issues |
| Public disclosure (coordinated) | After patch is available and deployers have had time to update |

For **low-severity** issues (e.g. minor information disclosure, hardening
improvements), the timeline may extend to 30–45 days.

If we need more information from you during the investigation, we will reach
out via the email address you used to contact us. Please respond promptly —
reports that go unanswered for 14 days may be closed.

---

## 📢 Disclosure Policy

We follow **Coordinated Vulnerability Disclosure (CVD)**:

1. You report the vulnerability to us privately.
2. We investigate, develop a fix, and prepare a security advisory.
3. We publish the patched release.
4. We publicly disclose the vulnerability details in the release notes and/or
   a GitHub Security Advisory — crediting you if you wish.

**We ask that you:**
- Give us a reasonable amount of time to fix the issue before any public
  disclosure (we target 21 days for critical issues).
- Avoid accessing, modifying, or deleting data that does not belong to you
  during testing.
- Limit testing to environments you own or have explicit permission to test.
  Do **not** test against the live demo at `syncx.pythonanywhere.com` in ways
  that could affect other users.

**We commit to:**
- Respond to your report promptly and keep you informed throughout the process.
- Not pursue legal action against researchers acting in good faith under this
  policy.
- Credit you publicly if you wish.

---

## 🛡 Security Best Practices for Deployers

If you are deploying College ERP in a real educational institution, the
following hardening steps are **strongly recommended**. The default development
configuration is **not safe for production use.**

---

### Django Settings

Never run with `DEBUG = True` in production. Set it explicitly in your
production settings:

```python
# production_settings.py
DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

Enable Django's built-in security middleware — all of these should be active:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',       # Never disable this
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Enable additional security settings:

```python
# Force HTTPS
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True            # HTTPS only
CSRF_COOKIE_SECURE = True               # HTTPS only
SESSION_COOKIE_HTTPONLY = True          # No JavaScript access
CSRF_COOKIE_HTTPONLY = True

# Clickjacking protection
X_FRAME_OPTIONS = 'DENY'

# Content type sniffing protection
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS filter (legacy browsers)
SECURE_BROWSER_XSS_FILTER = True
```

---

### Secret Key

The `SECRET_KEY` in `settings.py` must be:
- **Long** (50+ random characters)
- **Unique** per deployment
- **Never committed to version control**

Generate a new one:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Store it in an environment variable, never in source code:

```python
# settings.py
import os

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set.")
```

---

### Database

For production, replace the default SQLite database with PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',      # Enforce SSL for DB connections
        }
    }
}
```

Additional database hardening:
- Create a dedicated database user with only the permissions it needs
  (no superuser, no CREATE DATABASE)
- Enable PostgreSQL connection logging for audit trails
- Take regular automated backups
- Never expose the database port publicly — keep it behind a firewall

---

### Authentication

**Change all default passwords immediately** before going live:

```bash
python manage.py changepassword admin
```

Enforce a strong password policy. Add `django-password-validators` or
configure Django's built-in validators in `settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
```

**Session security:**

```python
SESSION_COOKIE_AGE = 3600          # 1 hour (seconds) — adjust per policy
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True
```

Consider adding **rate limiting / brute-force protection** on the login view
using `django-axes` or `django-ratelimit`:

```bash
pip install django-axes
```

```python
# settings.py
INSTALLED_APPS += ['axes']
MIDDLEWARE += ['axes.middleware.AxesMiddleware']
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'main_app.EmailBackend.EmailBackend',
]
AXES_FAILURE_LIMIT = 5             # Lock after 5 failed attempts
AXES_COOLOFF_TIME = 1              # Hours before lockout expires
```

---

### HTTPS & Headers

Always deploy behind HTTPS. Use a valid TLS certificate (free options:
Let's Encrypt via Certbot). If using PythonAnywhere, HTTPS is handled
automatically on custom domains.

Add a Content Security Policy (CSP) header to mitigate XSS. Using
`django-csp`:

```bash
pip install django-csp
```

```python
MIDDLEWARE += ['csp.middleware.CSPMiddleware']

CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC  = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net")
CSP_STYLE_SRC   = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net",
                   "fonts.googleapis.com")
CSP_FONT_SRC    = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC     = ("'self'", "data:")
```

---

### File Uploads

Profile photos are uploaded to the `media/` directory. Harden this:

```python
# Restrict allowed file types (add to your upload view or form)
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
MAX_UPLOAD_SIZE = 5 * 1024 * 1024   # 5 MB

# In production, serve media files from a separate domain or CDN
# Never serve media files through Django in production — use nginx or S3
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', '/var/www/college_erp/media/')
MEDIA_URL = '/media/'
```

Validate file types server-side — do not rely on the file extension alone:

```python
import magic  # python-magic library

def validate_image(file):
    mime = magic.from_buffer(file.read(1024), mime=True)
    if mime not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
        raise ValidationError("Only image files are allowed.")
    file.seek(0)
```

Never store uploaded files in a publicly web-accessible location where
they could be executed as scripts.

---

### Environment Variables

Store all secrets in environment variables — never in `settings.py` or
committed to version control:

```bash
# .env (never commit this file — it is in .gitignore)
DJANGO_SECRET_KEY=your-very-long-random-secret-key
DB_NAME=college_erp_prod
DB_USER=college_erp_user
DB_PASSWORD=strong-db-password
DB_HOST=localhost
RECAPTCHA_PUBLIC_KEY=your-recaptcha-site-key
RECAPTCHA_PRIVATE_KEY=your-recaptcha-secret-key
EMAIL_HOST_PASSWORD=your-email-app-password
```

Use `python-decouple` or `django-environ` to load these cleanly:

```bash
pip install python-decouple
```

```python
from decouple import config

SECRET_KEY = config('DJANGO_SECRET_KEY')
DB_PASSWORD = config('DB_PASSWORD')
DEBUG = config('DEBUG', default=False, cast=bool)
```

Confirm `.env` is in your `.gitignore` (it already is in this repo).

---

## ⚠️ Known Security Considerations

The following are known limitations that deployers should be aware of:

| Item | Details | Mitigation |
|------|---------|------------|
| **SQLite in development** | `db.sqlite3` is committed to the repo for development convenience. It contains demo data only — no real student records. | Switch to PostgreSQL before any production use. Delete `db.sqlite3` from production. |
| **Demo credentials in README** | The live demo credentials (studentone@student.com / staffone@staff.com) are public for evaluation purposes. | These are for the demo environment only. Never use these credentials in a real deployment. |
| **`DEBUG = True` in dev** | The development `settings.py` has `DEBUG = True` which exposes stack traces. | This is intentional for local development. Always set `DEBUG = False` in production. |
| **No rate limiting by default** | The login form does not have rate limiting out of the box, making it vulnerable to brute-force. | Add `django-axes` as described above before production deployment. |
| **Media files served by Django** | In development, Django serves uploaded media files directly. | In production, delegate media file serving to nginx, Apache, or a CDN like AWS S3. |
| **reCAPTCHA requires API keys** | Google reCAPTCHA is integrated but requires valid API keys to function. | Set `RECAPTCHA_PUBLIC_KEY` and `RECAPTCHA_PRIVATE_KEY` in your environment. Without them, the CAPTCHA check is bypassed. |

---

## 🔐 Security Features Built Into This Project

College ERP includes the following security measures by default:

| Feature | Implementation |
|---------|---------------|
| **CSRF protection** | Django's `CsrfViewMiddleware` is active — all POST forms use `{% csrf_token %}` |
| **Password hashing** | Django's `PBKDF2PasswordHasher` (SHA-256, 600,000 iterations) — never plain text |
| **SQL injection prevention** | All database queries use Django ORM parameterized queries — no raw SQL |
| **XSS prevention** | Django's template engine auto-escapes all variables by default |
| **Role-based access control** | Views are protected by user type (`user_type` check) — students cannot access staff or admin views |
| **Authentication required** | All sensitive views require `@login_required` or equivalent checks |
| **Google reCAPTCHA** | Login form includes reCAPTCHA v2 to block automated login attempts |
| **Clickjacking protection** | `XFrameOptionsMiddleware` prevents the app from being embedded in iframes |
| **Custom email authentication** | `EmailBackend.py` allows login via email — usernames are not exposed |
| **`.gitignore` hygiene** | `db.sqlite3`, `__pycache__`, `.env`, and media files are excluded from version control |

---

## 🏆 Hall of Fame

We are grateful to the following security researchers who responsibly disclosed
vulnerabilities and helped make College ERP safer:

*No vulnerabilities have been reported yet. Be the first! 🔍*

If you report a valid vulnerability and consent to being named, you will be
listed here with your name/handle and the nature of the finding.

---

## 📞 Contact

| Purpose | Contact |
|---------|---------|
| Security vulnerabilities | ansmajidali@gmail.com (**private — use for security only**) |
| General bugs | [GitHub Issues](https://github.com/Ansarimajid/College-ERP/issues) |
| Questions & ideas | [GitHub Discussions](https://github.com/Ansarimajid/College-ERP/discussions) |
| LinkedIn | [ansmajidali](https://www.linkedin.com/in/ansmajidali) |

---

<div align="center">

*This security policy is reviewed and updated with each major release.*
*Last updated: v2.0.0 — February 2026*

**Majid Ali Ansari** · [GitHub](https://github.com/Ansarimajid) · [ansmajidali@gmail.com](mailto:ansmajidali@gmail.com)

</div>
