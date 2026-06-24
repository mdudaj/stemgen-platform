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


def drop_postgres_text_pattern_indexes(cursor, table_name, column_name):
    cursor.execute(
        """
        SELECT quote_ident(index_namespace.nspname) || '.' || quote_ident(index_class.relname)
        FROM pg_index index
        JOIN pg_class index_class ON index_class.oid = index.indexrelid
        JOIN pg_namespace index_namespace ON index_namespace.oid = index_class.relnamespace
        JOIN pg_class table_class ON table_class.oid = index.indrelid
        JOIN unnest(index.indkey) WITH ORDINALITY AS index_columns(attribute_number, ordinal)
          ON true
        JOIN pg_attribute attribute
          ON attribute.attrelid = table_class.oid
         AND attribute.attnum = index_columns.attribute_number
        JOIN unnest(index.indclass) WITH ORDINALITY AS index_classes(operator_class_oid, ordinal)
          ON index_classes.ordinal = index_columns.ordinal
        JOIN pg_opclass operator_class ON operator_class.oid = index_classes.operator_class_oid
        WHERE table_class.oid = %s::regclass
          AND attribute.attname = %s
          AND operator_class.opcname IN ('varchar_pattern_ops', 'text_pattern_ops', 'bpchar_pattern_ops')
          AND NOT EXISTS (
              SELECT 1
              FROM pg_constraint pg_constraint_entry
              WHERE pg_constraint_entry.conindid = index.indexrelid
          )
        """,
        [table_name, column_name],
    )
    for (index_name,) in cursor.fetchall():
        cursor.execute(f"DROP INDEX IF EXISTS {index_name}")


def normalize_postgres_evidence_id_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        drop_postgres_text_pattern_indexes(cursor, "curriculum_curriculumsource", "source_id")
        cursor.execute(
            f"""
            ALTER TABLE curriculum_curriculumsource
            ALTER COLUMN source_id TYPE uuid
            USING {UUID_FROM_TEXT_SQL.format(column='source_id')}
            """
        )
        drop_postgres_text_pattern_indexes(cursor, "curriculum_curriculumsnapshot", "snapshot_id")
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
