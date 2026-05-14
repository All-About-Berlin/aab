from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("insurance", "0013_case_intent"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="site",
            field=models.CharField(blank=True, default="allaboutberlin.com", max_length=100),
        ),
    ]
