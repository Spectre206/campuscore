# Backup Strategy

## PostgreSQL Backup

CampusCore uses PostgreSQL. Backups are critical for data safety.

### Create a backup

```bash
pg_dump -U campuscore -d campuscore -h localhost > campuscore_backup_$(date +%Y%m%d_%H%M%S).sql
```

If you use Docker, run:

```bash
docker compose exec db pg_dump -U campuscore -d campuscore > backup.sql
```

### Restore from backup

```bash
psql -U campuscore -d campuscore -h localhost < campuscore_backup_YYYYMMDD_HHMMSS.sql
```

For Docker:

```bash
cat backup.sql | docker compose exec -T db psql -U campuscore -d campuscore
```

### Scheduled backups with cron

Add a cron job to automate daily backups. Edit crontab:

```bash
crontab -e
```

Add line to run backup at 2 AM daily:

```text
0 2 * * * /usr/bin/pg_dump -U campuscore -d campuscore -h localhost > /backups/campuscore_$(date +\%Y\%m\%d).sql
```

### Retention policy

- Keep daily backups for 7 days.
- Keep weekly backups for 4 weeks.
- Keep monthly backups for 6 months.

Use a script to delete old files or use cloud storage lifecycle rules.

### Storage recommendations

- Store backups in a separate location from the database server.
- Use encrypted storage (e.g., AWS S3 with SSE, or encrypted volume).
- Test restoration periodically.

## Redis Data

Redis data is ephemeral; no backup needed for Celery broker/results. If using Redis for cache, ensure data can be rebuilt.

## Environment & Secrets

- Keep `.env` files secure and backed up separately (e.g., password manager).