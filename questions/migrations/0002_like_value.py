from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionlike',
            name='value',
            field=models.SmallIntegerField(
                choices=[(1, 'Лайк'), (-1, 'Дизлайк')],
                default=1,
                verbose_name='Значение',
            ),
        ),
        migrations.AddField(
            model_name='answerlike',
            name='value',
            field=models.SmallIntegerField(
                choices=[(1, 'Лайк'), (-1, 'Дизлайк')],
                default=1,
                verbose_name='Значение',
            ),
        ),
    ]
