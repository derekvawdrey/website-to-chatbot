# Generated by Django 4.2.1 on 2023-05-21 04:09

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0010_embeddedcontent_content_to_embed'),
    ]

    operations = [
        migrations.AddField(
            model_name='embeddedcontent',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
