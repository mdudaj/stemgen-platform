# Generated to preserve the applied Slice 1 initial migration contract.

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("curriculum", "0002_curriculumsnapshot_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="curriculumsource",
            name="description",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
