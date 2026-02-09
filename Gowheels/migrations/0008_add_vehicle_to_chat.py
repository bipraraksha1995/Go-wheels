from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gowheels', '0007_vehicle_listing_type'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE gowheels_chat ADD COLUMN vehicle_id bigint NULL",
            reverse_sql="ALTER TABLE gowheels_chat DROP COLUMN vehicle_id"
        ),
        migrations.RunSQL(
            sql="ALTER TABLE gowheels_chat ADD CONSTRAINT gowheels_chat_vehicle_id_fk FOREIGN KEY (vehicle_id) REFERENCES gowheels_vehicle(id)",
            reverse_sql="ALTER TABLE gowheels_chat DROP FOREIGN KEY gowheels_chat_vehicle_id_fk"
        ),
    ]
