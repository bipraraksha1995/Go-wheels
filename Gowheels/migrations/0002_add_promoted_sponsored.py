from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gowheels', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='promoted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='sponsored',
            field=models.BooleanField(default=False),
        ),
    ]