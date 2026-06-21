# Generated to make source and snapshot evidence identifiers UUID-backed.

import uuid

from django.db import migrations
from django.db import models


UUID_FROM_TEXT_SQL = """
CASE
  WHEN {column}::text ~* '^[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}$'
    THEN {column}::uuid
  ELSE (
    substr(md5({column}::text), 1, 8) || '-' ||
    substr(md5({column}::text), 9, 4) || '-' ||
    substr(md5({column}::text), 13, 4) || '-' ||
    substr(md5({column}::text), 17, 4) || '-' ||
    substr(md5({column}::text), 21, 12)
  )::uuid
END
"""


def normalize_postgres_evidence_id_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            f"""
            ALTER TABLE curriculum_curriculumsource
            ALTER COLUMN source_id TYPE uuid
            USING {UUID_FROM_TEXT_SQL.format(column='source_id')}
            """
        )
        cursor.execute(
            f"""
            ALTER TABLE curriculum_curriculumsnapshot
            ALTER COLUMN snapshot_id TYPE uuid
            USING {UUID_FROM_TEXT_SQL.format(column='snapshot_id')}
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0004_normalize_evidence_id_columns"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(normalize_postgres_evidence_id_columns, migrations.RunPython.noop),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="curriculumsource",
                    name="source_id",
                    field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                migrations.AlterField(
                    model_name="curriculumsnapshot",
                    name="snapshot_id",
                    field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
            ],
        ),
    ]
