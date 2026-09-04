# Production Deployment Checklist

Before deploying CampusCore to production, ensure the following are set in the environment:

- `DEBUG=False`
- `SECRET_KEY` is a strong, unique secret
- `ALLOWED_HOSTS` includes the production domain(s)
- `USE_SECURE_COOKIES=True` (enables HTTPS-related settings)
- `EMAIL_BACKEND` set to a production email backend (e.g., `django.core.mail.backends.smtp.EmailBackend`)
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` configured for SMTP
- `DB_HOST`, `DB_USER`, `DB_PASSWORD` point to production database
- `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` point to production Redis
- `GROQ_API_KEY` and `AI_PROVIDER` set if using AI features
- Throttle rates (`THROTTLE_ANON_RATE`, `THROTTLE_USER_RATE`) adjusted for production

Run `python manage.py check --deploy` after setting these to verify no critical warnings.