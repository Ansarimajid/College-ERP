# Contributing to College ERP 🎓

First off — thank you for taking the time to contribute! 🙌

College ERP is an open-source Django web application that helps educational
institutions manage students, staff, attendance, results, and administration
in one unified platform. Every contribution — whether it's a typo fix, a bug
report, or a full feature — makes this project more valuable for institutions
and developers around the world.

Please read this guide carefully before opening an issue or submitting a pull
request. It will save everyone time and keep the project healthy.

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Who Can Contribute](#-who-can-contribute)
- [Ways to Contribute](#-ways-to-contribute)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Fork and Clone](#fork-and-clone)
  - [Environment Setup](#environment-setup)
  - [Running Locally](#running-locally)
- [Project Structure](#-project-structure)
- [Understanding the Codebase](#-understanding-the-codebase)
- [Development Workflow](#-development-workflow)
  - [Branching Strategy](#branching-strategy)
  - [Making Changes](#making-changes)
  - [Keeping Your Fork in Sync](#keeping-your-fork-in-sync)
- [Commit Message Guidelines](#-commit-message-guidelines)
- [Pull Request Process](#-pull-request-process)
  - [Before You Submit](#before-you-submit)
  - [PR Description Template](#pr-description-template)
  - [Review Process](#review-process)
- [Issue Reporting](#-issue-reporting)
  - [Bug Reports](#bug-reports)
  - [Feature Requests](#feature-requests)
  - [Security Vulnerabilities](#security-vulnerabilities)
- [Coding Standards](#-coding-standards)
  - [Python & Django](#python--django)
  - [Templates & HTML](#templates--html)
  - [JavaScript](#javascript)
  - [CSS & Styling](#css--styling)
  - [Database & Models](#database--models)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Roadmap & Priorities](#-roadmap--priorities)
- [Community & Support](#-community--support)
- [Recognition](#-recognition)

---

## 📜 Code of Conduct

This project follows the
[Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating in this project, you agree to abide by its terms.

We are committed to making this a welcoming space for everyone regardless of
experience level, background, or identity. Harassment, discrimination, or
disrespectful behavior of any kind will not be tolerated.

**To report a violation:** Email **ansmajidali@gmail.com** — all reports are
handled confidentially.

---

## 👥 Who Can Contribute

**Everyone is welcome.** You do not need to be an experienced Django developer
to contribute. Here's a rough guide by experience level:

| Level | Good starting points |
|-------|----------------------|
| **Beginner** | Fix typos in docs, improve README sections, report bugs, answer questions in Discussions |
| **Intermediate** | Fix labeled issues, improve UI templates, add form validations, write tests |
| **Advanced** | Implement Roadmap features, refactor views, improve performance, add APIs |

If you're unsure where to start, look for issues tagged
[`good first issue`](https://github.com/Ansarimajid/College-ERP/issues?q=label%3A%22good+first+issue%22)
or
[`help wanted`](https://github.com/Ansarimajid/College-ERP/issues?q=label%3A%22help+wanted%22).

---

## 🤝 Ways to Contribute

Contributing goes well beyond writing code:

### 🐛 Report bugs
Found something broken on the [live demo](https://syncx.pythonanywhere.com)
or while running locally? Open an issue with detailed steps to reproduce.

### 💡 Suggest features
Have an idea not on the Roadmap? Start a
[GitHub Discussion](https://github.com/Ansarimajid/College-ERP/discussions)
first so the community can weigh in before it becomes a formal issue.

### 🔧 Fix bugs
Browse open issues labeled
[`bug`](https://github.com/Ansarimajid/College-ERP/issues?q=label%3Abug)
and submit a fix via pull request.

### ✨ Build features
Pick something from the [Roadmap](#-roadmap--priorities) or a
[`feature request`](https://github.com/Ansarimajid/College-ERP/issues?q=label%3Aenhancement)
issue. Comment on the issue first to avoid duplicate work.

### 📖 Improve documentation
Better setup guides, docstrings, code comments, or wiki pages all count and
are just as valuable as code contributions.

### 🧪 Write tests
The project has minimal test coverage. Adding unit tests or integration tests
for existing features is a high-value contribution.

### 🎨 Improve UI/UX
Improve templates, fix responsive layout issues, enhance accessibility, or
modernize the Bootstrap components.

### 🌍 Translate the app
Help localize the interface for non-English speaking institutions by adding
Django i18n translations.

### 💬 Help other contributors
Answer questions in
[GitHub Discussions](https://github.com/Ansarimajid/College-ERP/discussions),
review open pull requests, or mentor new contributors.

---

## 🚀 Getting Started

### Prerequisites

Ensure the following are installed on your system:

| Tool | Version | Purpose |
|------|---------|---------|
| [Git](https://git-scm.com/) | Any recent | Version control |
| [Python](https://www.python.org/downloads/) | 3.8+ | Runtime |
| [pip](https://pip.pypa.io/) | Latest | Package manager |
| [Conda](https://docs.conda.io/) *(optional)* | Any | Recommended env manager |

You can verify your versions:

```bash
git --version
python --version   # or python3 --version on macOS/Linux
pip --version
```

---

### Fork and Clone

**Step 1 — Fork the repository**

Click the **Fork** button at the top-right of the
[College-ERP repo](https://github.com/Ansarimajid/College-ERP).
This creates your own copy under your GitHub account.

**Step 2 — Clone your fork**

```bash
git clone https://github.com/YOUR_USERNAME/College-ERP.git
cd College-ERP
```

**Step 3 — Add the upstream remote**

This lets you pull future changes from the original repo:

```bash
git remote add upstream https://github.com/Ansarimajid/College-ERP.git

# Verify remotes
git remote -v
# origin    https://github.com/YOUR_USERNAME/College-ERP.git (fetch)
# upstream  https://github.com/Ansarimajid/College-ERP.git  (fetch)
```

---

### Environment Setup

Choose one of two methods:

#### Option A — Conda (Recommended)

A `college-erp.yml` file is included in the root. This sets up a complete
environment with all dependencies:

```bash
conda env create -f college-erp.yml
conda activate Django-env
```

To update the environment after pulling changes:

```bash
conda env update -f college-erp.yml --prune
```

#### Option B — Python venv

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv venv
source venv/scripts/activate
pip install -r requirements.txt
```

> 💡 **Tip:** Always activate your environment before working on the project.
> You should see `(Django-env)` or `(venv)` in your terminal prompt.

---

### Running Locally

**Step 1 — Apply database migrations**

```bash
python manage.py migrate
```

**Step 2 — Create a superuser (Admin / HOD)**

```bash
python manage.py createsuperuser
```

Follow the prompts to set your email and password.

**Step 3 — Start the development server**

```bash
# macOS / Linux
python3 manage.py runserver

# Windows
python manage.py runserver
```

**Step 4 — Open in browser**

Visit `http://127.0.0.1:8000` — you should see the College ERP login page.

> **Reference credentials** (live demo only — use your superuser locally):
>
> | Role | Email | Password |
> |------|-------|----------|
> | Student | studentone@student.com | studentone |
> | Staff | staffone@staff.com | staffone |

---

## 🗂 Project Structure

```
College-ERP/
│
├── college_management_system/      # Django project configuration
│   ├── settings.py                 # App settings, database, static files
│   ├── urls.py                     # Root URL dispatcher
│   └── wsgi.py                     # WSGI entry point for deployment
│
├── main_app/                       # Core Django application
│   ├── migrations/                 # Database migration files
│   ├── templates/
│   │   └── main_app/               # All HTML templates
│   │       ├── admin_templates/    # HOD/Admin views
│   │       ├── staff_templates/    # Staff views
│   │       └── student_templates/  # Student views
│   ├── static/                     # App-level static files
│   ├── models.py                   # All database models
│   ├── views.py                    # All role-based view logic
│   ├── forms.py                    # Django forms
│   ├── urls.py                     # App-level URL routes
│   └── EmailBackend.py             # Custom email authentication
│
├── media/                          # User-uploaded files (profile photos)
├── Showcase/                       # Screenshots used in README
├── reports_and_resource/           # Supporting documents
│
├── manage.py                       # Django management script
├── requirements.txt                # Python dependencies
├── college-erp.yml                 # Conda environment definition
├── Procfile                        # Deployment config (PythonAnywhere)
├── db.sqlite3                      # SQLite database (development only)
├── .gitignore
├── LICENSE
├── README.md
├── CODE_OF_CONDUCT.md
└── CONTRIBUTING.md                 # This file
```

---

## 🧠 Understanding the Codebase

### Three User Roles

The entire application is built around three user types, each with its own
login, dashboard, and permission scope:

| Role | Description | Key Capabilities |
|------|-------------|-----------------|
| **HODAdmin** | Head of Department / Administrator | Full CRUD on staff, students, courses, subjects, sessions; view all attendance & results; manage leave approvals & feedback |
| **Staff** | Teaching faculty | Mark attendance, enter results, apply for leave, send feedback to admin |
| **Student** | Enrolled students | View own attendance & results, apply for leave, send feedback |

### Key Models (`main_app/models.py`)

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extended Django user with `user_type` (1=Admin, 2=Staff, 3=Student) |
| `AdminHOD` | Admin profile linked to CustomUser |
| `Staffs` | Staff profile with department/address info |
| `Students` | Student profile linked to course, session, profile pic |
| `Courses` | Academic course (e.g. B.Sc Computer Science) |
| `Subjects` | Subject under a course, assigned to a staff member |
| `SessionYearModel` | Academic year/session tracking |
| `Attendance` | Attendance session record per subject per date |
| `AttendanceReport` | Individual student attendance status per session |
| `LeaveReportStaff` / `LeaveReportStudent` | Leave request records |
| `FeedbackStaffs` / `FeedbackStudent` | Feedback messages to admin |
| `StudentResult` | Exam marks per student per subject |

### Authentication Flow

The project uses a custom authentication backend (`EmailBackend.py`) that
allows login via email instead of username. Login redirects are handled based
on `user_type` — make sure any auth changes preserve this routing logic.

---

## 🔄 Development Workflow

### Branching Strategy

**Never commit directly to `main`.** All changes go through branches and
pull requests.

```
main                  ← stable, production-ready code
 └── feature/xyz      ← your new feature
 └── fix/xyz          ← your bug fix
 └── docs/xyz         ← documentation improvements
```

### Branch naming convention

| Type | Pattern | Example |
|------|---------|---------|
| New feature | `feature/short-description` | `feature/sms-notifications` |
| Bug fix | `fix/short-description` | `fix/attendance-duplicate-date` |
| Documentation | `docs/short-description` | `docs/improve-setup-guide` |
| UI improvement | `ui/short-description` | `ui/mobile-dashboard-layout` |
| Tests | `test/short-description` | `test/leave-model-unit-tests` |
| Refactor | `refactor/short-description` | `refactor/views-split-by-role` |

Use **lowercase**, **hyphens** (not underscores), and keep it short but descriptive.

### Making Changes

```bash
# 1. Sync with upstream before starting
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create your branch
git checkout -b feature/your-feature-name

# 3. Make your changes, then stage and commit
git add .
git commit -m "feat: add SMS notification on leave approval"

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Open a Pull Request on GitHub
```

### Keeping Your Fork in Sync

If the main repo has been updated while you were working:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/your-feature-name
git rebase main
```

Resolve any conflicts, then continue:

```bash
git rebase --continue
git push origin feature/your-feature-name --force-with-lease
```

---

## ✍️ Commit Message Guidelines

Clear commit messages make the project history readable and help reviewers
understand your changes at a glance.

### Format

```
type: concise summary in present tense (max 72 characters)

Optional body: explain WHY this change was made, not just what.
Wrap at 72 characters. Leave a blank line between subject and body.

Optional footer:
Closes #42
Fixes #17
Co-authored-by: Name <email>
```

### Types

| Type | Use for |
|------|---------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only changes |
| `style` | Formatting, whitespace — no logic change |
| `refactor` | Code restructuring — no behavior change |
| `test` | Adding or fixing tests |
| `chore` | Build process, dependency updates, tooling |
| `ui` | Template or frontend changes |
| `perf` | Performance improvements |

### Good examples

```bash
feat: add PDF export for student attendance report
fix: resolve leave approval not sending email notification
docs: add Windows setup instructions to CONTRIBUTING
test: add unit tests for StudentResult model
refactor: split views.py into role-based modules
ui: fix staff dashboard table overflow on mobile
chore: update Django to 4.2.x in requirements.txt
```

### Bad examples

```bash
fixed bug           # too vague — which bug?
WIP                 # not a real commit message
update              # meaningless
added stuff         # what stuff?
```

---

## 📬 Pull Request Process

### Before You Submit

Run through this checklist before opening your PR:

**Functionality**
- [ ] The application runs without errors (`python manage.py runserver`)
- [ ] Your feature/fix works as intended — test it manually
- [ ] All three user roles (Admin, Staff, Student) still function correctly
- [ ] The live demo use-cases are not broken

**Code quality**
- [ ] Code follows the [Coding Standards](#-coding-standards) below
- [ ] No debug `print()` statements or `console.log()` left in
- [ ] No commented-out dead code left behind
- [ ] No hardcoded credentials, tokens, or `SECRET_KEY` values committed

**Database**
- [ ] If you changed any model, migrations are included
  (`python manage.py makemigrations` was run)
- [ ] Migrations apply cleanly (`python manage.py migrate`)

**Dependencies**
- [ ] If you added a new package, `requirements.txt` is updated
- [ ] If using Conda, `college-erp.yml` is updated

**Documentation**
- [ ] New functions/classes have docstrings
- [ ] README updated if the setup process changed
- [ ] Any new settings or environment variables are documented

---

### PR Description Template

Use this structure when writing your PR description:

```markdown
## What does this PR do?
A clear one-paragraph description of the change.

## Why is this change needed?
Explain the problem being solved or the value being added.

## How was it implemented?
Brief technical notes — key design decisions, trade-offs made.

## How to test it?
Step-by-step instructions to verify the change works.
1. Log in as Staff at http://127.0.0.1:8000
2. Navigate to Leave Applications
3. ...

## Screenshots (if UI change)
Before | After
--- | ---
[screenshot] | [screenshot]

## Related issues
Closes #issue_number
```

---

### Review Process

1. Once you open a PR, the maintainer will review within **48–72 hours**.
2. You may receive review comments — address them by pushing new commits to
   the same branch (don't close and reopen the PR).
3. Once approved, the maintainer will merge your PR into `main`.
4. Your branch can be safely deleted after merging.

**Response time expectations:**
- Simple bug fixes / docs: reviewed within 48 hours
- New features: may take up to 1 week depending on complexity
- Large refactors: discussed in a GitHub Discussion before review begins

---

## 🐛 Issue Reporting

Before opening a new issue, please
[search existing issues](https://github.com/Ansarimajid/College-ERP/issues)
to avoid duplicates.

### Bug Reports

A good bug report enables someone else to reproduce the problem. Include:

```markdown
**Describe the bug**
A clear description of what the bug is.

**Steps to reproduce**
1. Log in as [role] at [URL]
2. Navigate to [page]
3. Click [button/action]
4. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened (include error messages verbatim).

**Screenshots**
If applicable, add screenshots.

**Environment**
- OS: [e.g. Windows 11, Ubuntu 22.04, macOS 14]
- Python version: [e.g. 3.10.6]
- Browser: [e.g. Chrome 124, Firefox 125]
- Encountered on: [ ] Live demo  [ ] Local setup

**Additional context**
Anything else that might be relevant.
```

### Feature Requests

For new features, **please start a
[GitHub Discussion](https://github.com/Ansarimajid/College-ERP/discussions)
first** rather than opening an issue directly. This lets the community
validate the idea before development begins. Check the
[Roadmap](#-roadmap--priorities) — it may already be planned.

Once a feature request discussion reaches consensus, a formal issue will be
created and labeled `enhancement`.

### Security Vulnerabilities

**Do NOT report security vulnerabilities in public issues.**

If you discover a security vulnerability, please email
**ansmajidali@gmail.com** directly with:

- A description of the vulnerability
- Steps to reproduce it
- Potential impact
- Any suggested fix (optional)

You will receive a response within 72 hours. Please give us reasonable time
to address the issue before any public disclosure.

---

## 🧹 Coding Standards

### Python & Django

Follow [PEP 8](https://pep8.org/) for all Python code.

**Views** — Keep views thin. Move business logic into model methods or
utility functions:

```python
# ❌ Bad — business logic in the view
def leave_approve_view(request, leave_id):
    leave = LeaveReportStudent.objects.get(id=leave_id)
    total_leaves = LeaveReportStudent.objects.filter(
        student=leave.student, leave_status=1
    ).count()
    if total_leaves >= 10:
        # complex logic here...
        pass

# ✅ Good — logic in the model
def leave_approve_view(request, leave_id):
    leave = get_object_or_404(LeaveReportStudent, id=leave_id)
    leave.approve()   # method on the model handles the logic
    messages.success(request, "Leave approved.")
    return redirect("admin_leave_view")
```

**Models** — Add `verbose_name`, `__str__`, and ordering where appropriate:

```python
class Students(models.Model):
    admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    course_id = models.ForeignKey(Courses, on_delete=models.DO_NOTHING,
                                   verbose_name="Course")
    session_year_id = models.ForeignKey(SessionYearModel,
                                         on_delete=models.CASCADE,
                                         verbose_name="Session Year")

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ["admin__first_name"]

    def __str__(self):
        return f"{self.admin.first_name} {self.admin.last_name}"
```

**Use `get_object_or_404`** instead of bare `.get()` in views to return
proper 404 responses:

```python
# ❌ Bad
student = Students.objects.get(id=student_id)

# ✅ Good
student = get_object_or_404(Students, id=student_id)
```

**Use Django messages framework** for user feedback — not custom session
variables:

```python
from django.contrib import messages

messages.success(request, "Student added successfully.")
messages.error(request, "Failed to add student. Please try again.")
```

**Docstrings** — Add to all new functions and classes:

```python
def get_attendance_percentage(student, subject):
    """
    Calculate attendance percentage for a student in a specific subject.

    Args:
        student (Students): The student instance.
        subject (Subjects): The subject instance.

    Returns:
        float: Attendance percentage rounded to 2 decimal places.
                Returns 0.0 if no attendance records exist.
    """
    total = Attendance.objects.filter(subject=subject).count()
    if total == 0:
        return 0.0
    present = AttendanceReport.objects.filter(
        student=student,
        attendance__subject=subject,
        status=True
    ).count()
    return round((present / total) * 100, 2)
```

**Avoid raw SQL** — use Django's ORM unless there is a measurable performance
reason to do otherwise. If raw SQL is necessary, add a comment explaining why.

**Class-based views (CBVs)** — The project already uses CBVs for result
management. New complex views should use CBVs where it reduces repetition.
Simple views (quick form processes) can remain function-based.

---

### Templates & HTML

- Keep templates in `main_app/templates/main_app/` under the appropriate
  role subfolder (`admin_templates/`, `staff_templates/`, `student_templates/`)
- Use Django template tags and filters — avoid embedding raw Python logic
- Use `{% url 'name' %}` for all links — never hardcode URLs
- Extend the base template using `{% extends "base.html" %}` and define
  content in `{% block content %}{% endblock %}`
- Always use `{% csrf_token %}` in every `<form>` that submits data
- Test UI changes at mobile width (375px) as well as desktop

```html
{# ❌ Bad — hardcoded URL #}
<a href="/student/attendance/">View Attendance</a>

{# ✅ Good — named URL #}
<a href="{% url 'student_view_attendance' %}">View Attendance</a>
```

---

### JavaScript

- The project uses vanilla JS and jQuery (included via Bootstrap) — do **not**
  add new JS frameworks or libraries without prior discussion
- Place scripts in the appropriate `static/` directory — not inline in templates
  (except for small, page-specific event handlers)
- Use `$(document).ready()` for jQuery code
- Add `// Purpose:` comments at the top of non-trivial JS functions

---

### CSS & Styling

- The project uses Bootstrap — use Bootstrap utility classes before writing
  custom CSS
- Custom CSS goes in the relevant static file — not inline `style=""` attributes
- Do not override Bootstrap variables globally without discussion — changes
  affect every page
- Maintain the existing color scheme and visual consistency

---

### Database & Models

- **Always run `makemigrations`** after any model change:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- **Never delete migration files** — create new migrations instead
- **Never edit an existing migration** that has already been committed —
  create a new one
- **Do not commit `db.sqlite3`** — it is in `.gitignore` and contains local
  data that should not be shared
- Name new models and fields descriptively — prefer `leave_status` over `status`
  when the context matters

---

## 🧪 Testing

The project currently has minimal test coverage. Adding tests is one of the
most impactful contributions you can make.

### Running existing tests

```bash
python manage.py test main_app
```

### Writing new tests

Place test files in `main_app/tests/` (create the directory if needed).
Organize by model or view:

```
main_app/
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_views_admin.py
    ├── test_views_staff.py
    └── test_views_student.py
```

**Example test structure:**

```python
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from main_app.models import Courses, Students, SessionYearModel

User = get_user_model()


class StudentModelTest(TestCase):
    """Tests for the Students model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="test_student",
            email="student@test.com",
            password="testpass123",
            user_type=3
        )
        self.course = Courses.objects.create(course_name="B.Sc CS")
        self.session = SessionYearModel.objects.create(
            session_start_year="2024-06-01",
            session_end_year="2025-05-31"
        )

    def test_student_str_representation(self):
        """Student __str__ should return full name."""
        self.user.first_name = "Majid"
        self.user.last_name = "Ansari"
        self.user.save()
        student = Students.objects.get(admin=self.user)
        self.assertEqual(str(student), "Majid Ansari")


class AdminLeaveApprovalTest(TestCase):
    """Tests for the leave approval workflow."""

    def setUp(self):
        self.client = Client()
        # Create admin user and log in
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass"
        )
        self.client.login(email="admin@test.com", password="adminpass")

    def test_leave_approve_redirects(self):
        """Approving a leave should redirect to leave list."""
        # ... test implementation
        pass
```

**What to test (priority order):**
1. Model `__str__` methods and key model methods
2. View responses (status codes, redirects, template used)
3. Form validation (valid and invalid data)
4. Permission checks (students can't access admin views)
5. Edge cases (empty attendance, no results yet, etc.)

---

## 📖 Documentation

Good documentation is as important as good code. When contributing:

- **Docstrings** — Add to every new function, method, and class using the
  Google-style format shown in the Coding Standards section
- **Inline comments** — Explain *why* something is done when the code alone
  isn't clear. Do not comment *what* the code does — that should be obvious
- **README** — If your change affects the setup process, deployment, or
  feature list, update `README.md` accordingly
- **This file** — If you notice outdated information in `CONTRIBUTING.md`,
  please open a PR to fix it

---

## 🗺️ Roadmap & Priorities

These upcoming features are most in need of contributors. Pick one and comment
on the related issue before starting, to avoid duplicate work.

| Priority | Feature | Complexity | Skills needed |
|----------|---------|------------|---------------|
| 🔴 High | SMS notifications on leave approval/rejection | Medium | Twilio or similar API, Django signals |
| 🔴 High | Advanced analytics dashboard with PDF/Excel export | High | ReportLab or WeasyPrint, Chart.js |
| 🟡 Medium | Online examination module | High | Django models, timed views, result calculation |
| 🟡 Medium | Fee management & payment tracking | High | Django models, financial logic |
| 🟡 Medium | Timetable generator | Medium | Scheduling logic, UI calendar |
| 🟡 Medium | Parent portal (read-only attendance & results view) | Medium | New user role, permission system |
| 🟢 Low | Library management integration | High | New app module |
| 🟢 Low | Django REST Framework API layer | High | DRF, serializers, token auth |
| 🟢 Low | Dark mode UI option | Low | CSS variables, localStorage |
| 🟢 Low | i18n / Hindi & Urdu language support | Medium | Django i18n, translation files |

If you want to propose something not on this list, start a
[Discussion](https://github.com/Ansarimajid/College-ERP/discussions) first.

---

## 💬 Community & Support

| Channel | Use for |
|---------|---------|
| [GitHub Discussions](https://github.com/Ansarimajid/College-ERP/discussions) | Feature ideas, setup questions, general conversation |
| [GitHub Issues](https://github.com/Ansarimajid/College-ERP/issues) | Confirmed bugs and approved feature requests only |
| [Email](mailto:ansmajidali@gmail.com) | Security vulnerabilities, Code of Conduct reports |

**Response times:**
- GitHub Discussions: within 24–48 hours
- GitHub Issues: within 48 hours
- Email: within 72 hours

---

## 🏆 Recognition

All contributors are recognized in the following ways:

- Listed as a contributor in GitHub's
  [Contributors graph](https://github.com/Ansarimajid/College-ERP/graphs/contributors)
- Significant contributions are acknowledged in release notes
- First-time contributors receive a personal thank-you comment on their
  merged PR

**Contribution types we recognize equally:**
code · documentation · tests · bug reports · feature ideas · community support

---

<div align="center">

**Thank you for being part of College ERP. 🎓**

*Your contribution — however small — helps students and institutions
around the world.*

⭐ If this project has been useful to you, consider
[starring the repository](https://github.com/Ansarimajid/College-ERP)!

</div>
