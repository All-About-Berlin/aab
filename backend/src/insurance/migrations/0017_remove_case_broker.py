from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("insurance", "0016_alter_feedbacknotification_delivery_date"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="case",
            name="broker",
        ),
    ]
