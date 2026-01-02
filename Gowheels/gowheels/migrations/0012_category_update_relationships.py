from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gowheels', '0011_vehicleclick'),
    ]

    operations = [
        # Create Category model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('group1', 'Group 1'), ('group2', 'Group 2'), ('group3', 'Group 3')], max_length=20)),
                ('image', models.ImageField(upload_to='categories/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        # Add category foreign key to BrandImage
        migrations.AddField(
            model_name='brandimage',
            name='category_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='brands', to='gowheels.category'),
        ),
    ]