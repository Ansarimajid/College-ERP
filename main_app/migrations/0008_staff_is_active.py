from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('main_app', '0007_attendance_status_safety_net'),
    ]
    operations = [
        migrations.AddField(
            model_name='staff',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
