# Generated by Django 2.2.10 on 2020-03-27 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("zgw_consumers", "0006_update_oas_auth"),
    ]

    operations = [
        migrations.AddField(
            model_name="service",
            name="nlx",
            field=models.URLField(
                blank=True,
                help_text="NLX inway address",
                max_length=255,
                verbose_name="NLX url",
            ),
        ),
    ]