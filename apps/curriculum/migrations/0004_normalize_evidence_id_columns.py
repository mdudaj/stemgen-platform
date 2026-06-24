# Generated to recover databases that applied the transient UUID ID contract.

from django.db import migrations


def normalize_postgres_evidence_id_columns(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE curriculum_curriculumsource
            ALTER COLUMN source_id TYPE varchar(120)
            USING source_id::varchar
            """
        )
        cursor.execute(
            """
            ALTER TABLE curriculum_curriculumsnapshot
            ALTER COLUMN snapshot_id TYPE varchar(120)
            USING snapshot_id::varchar
            """
        )


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0003_curriculumsource_description"),
    ]

    operations = [
        migrations.RunPython(normalize_postgres_evidence_id_columns, migrations.RunPython.noop),
    ]
