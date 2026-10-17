import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("forum", "0003_reply_modification_date_reply_removal_date_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Thread",
            new_name="Post",
        ),
        migrations.RenameField(
            model_name="reply",
            old_name="thread",
            new_name="post",
        ),
        migrations.AlterField(
            model_name="post",
            name="author",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="forum_posts",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
