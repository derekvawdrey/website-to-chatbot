# Generated by Django 4.2.1 on 2023-05-21 03:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0007_remove_scrapedpage_date_embedded_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmbeddedContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('embedding', models.TextField(default='')),
                ('is_embedded', models.BooleanField(default=False)),
                ('date_embedded', models.DateTimeField(auto_now_add=True)),
                ('related_scraped_page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scraper.scrapedpage')),
            ],
        ),
    ]
