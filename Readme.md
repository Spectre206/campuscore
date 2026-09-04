<div align="center">

# 🎓 CampusCore

**A modern, AI-powered education management platform**

Streamline academics, attendance, assessments, and communication — all in one place.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=flat-square&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Celery-DC382D?style=flat-square&logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

[Features](#-features) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Docs](#-api-documentation) • [Documentation](#-documentation)

</div>

---

## 📖 Overview

**CampusCore** is a full-featured education management system built for institutions that need a reliable, extensible backbone for academic operations. It brings together academic structure, attendance, assessments, role-based dashboards, notifications, and an AI-powered quiz generator into a single Django-based platform — designed to run comfortably in local development and scale cleanly with Docker.

---

## ✨ Features

| Category | Capabilities |
|---|---|
| 🏫 **Academic Structure** | Departments, Programs, Courses, Sections, and Enrollments |
| 🗓️ **Attendance** | Tracking workflows for both teachers and students |
| 📝 **Assessments & Grades** | Structured grading and assessment management |
| 👥 **Role-Based Dashboards** | Tailored views for Admins, Teachers, and Students |
| 🔔 **Notifications** | In-app and email notifications, delivered asynchronously via Celery |
| 🤖 **AI Quiz Generator** | Groq-powered quiz generation with a mock provider fallback for offline dev |
| 🔌 **REST API v1** | Fully documented with OpenAPI, Swagger UI, and ReDoc |
| 🐳 **Docker-First** | Complete Docker & Docker Compose setup for reproducible environments |

---

## 🛠 Tech Stack

<table>
<tr>
<td valign="top" width="50%">

**Backend**
- Python
- Django 6.1 + Django REST Framework

**Database**
- PostgreSQL 16

**Async / Background Jobs**
- Celery + Redis

</td>
<td valign="top" width="50%">

**AI**
- Groq (with local mock provider fallback)

**Frontend**
- Django Templates + HTMX + Bootstrap 5

**Testing**
- Django's built-in test runner (`unittest`-style via `TestCase`)

**CI/CD**
- GitHub Actions

</td>
</tr>
</table>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- PostgreSQL 16
- Redis

### Local Installation

**1. Clone the repository**

```bash
git clone https://github.com/Spectre206/campuscore.git
cd campuscore
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

```bash
cp .env.example .env
# Edit .env with your SECRET_KEY, database credentials, and other settings
```

**5. Run database migrations**

```bash
python manage.py migrate
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

**7. Start Redis** *(if not already running)*

```bash
redis-server
```

**8. Start the Celery worker** *(for background tasks)*

```bash
celery -A config worker -l info
```

**9. Run the development server**

```bash
python manage.py runserver
```

The app will be available at **http://127.0.0.1:8000/**

---

### 🐳 Setup with Docker

```bash
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

The app will be available at **http://localhost:8000/**

---

## ✅ Running Tests

```bash
python manage.py test
```

## 🧹 Linting & Formatting

```bash
ruff format .
ruff check . --fix
```

---

## 📚 API Documentation

| Resource | Path |
|---|---|
| Swagger UI | `/api/docs/` |
| ReDoc | `/api/redoc/` |
| OpenAPI Schema | `/api/schema/` |

---

## 📂 Documentation

- [Master Roadmap](docs/MASTER_ROADMAP.md)
- [Backup Strategy](docs/operations/backup.md)
- [Production Checklist](docs/operations/production-checklist.md)
- Version-specific docs available in [`docs/versions/`](docs/versions/)

---

## 📁 Project Structure

```
campuscore/
├── academics/          # Departments, Programs, Courses, Sections, Enrollments
├── accounts/           # Auth, roles, and user management
├── ai_service/         # AI quiz generation (Groq + mock provider)
├── config/             # Django project settings & Celery config
├── docs/               # Project documentation
├── notifications/      # In-app & email notifications
├── static/css/         # Static assets
├── templates/          # Django templates (HTMX + Bootstrap 5)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

Built with 🐍 Django and ☕ persistence

</div>