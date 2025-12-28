# Alembic Database Migrations

**Purpose**: Version control for database schema changes in DigiDoc OCR Service.

## Quick Start

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

### View current migration status:
```bash
alembic current
```

### View migration history:
```bash
alembic history
```

## Migration Workflow

1. **Modify models** in `ocr_service/database/models.py`
2. **Generate migration**: `alembic revision --autogenerate -m "description"`
3. **Review migration** in `alembic/versions/`
4. **Test migration**: `alembic upgrade head`
5. **Commit** migration file to Git

## Best Practices

- Always review auto-generated migrations before applying
- Test migrations on a copy of production data
- Never edit existing migration files (create new ones)
- Keep migrations small and focused
- Document breaking changes in migration comments

## Configuration

- Database URL: Set via `OCR_DATABASE_URL` environment variable or defaults to SQLite
- Models: Imported from `ocr_service.database.models`
- Migration directory: `alembic/versions/`

## Troubleshooting

### Migration conflicts:
If migrations conflict, use `alembic merge` to create a merge migration.

### Database out of sync:
If database schema doesn't match models:
1. Check current migration: `alembic current`
2. Check model state: Review `models.py`
3. Create new migration: `alembic revision --autogenerate -m "sync schema"`

