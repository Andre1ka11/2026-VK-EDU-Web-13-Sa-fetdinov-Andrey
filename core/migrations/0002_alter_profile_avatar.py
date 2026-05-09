from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=core.models.avatar_upload_path,
                verbose_name='Аватар',
            ),
        ),
    ]
