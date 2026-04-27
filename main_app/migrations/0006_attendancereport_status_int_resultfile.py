from django.db import migrations, models
import django.db.models.deletion


def convert_status_to_smallint(apps, schema_editor):
    """
    PostgreSQL cannot cast boolean → smallint with a bare ::smallint cast.
    SQLite already stores BooleanField as 0/1 integers, so no SQL is needed there.
    """
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute("""
            ALTER TABLE main_app_attendancereport
            ALTER COLUMN status TYPE smallint
            USING CASE WHEN status THEN 1 ELSE 0 END
        """)
    # sqlite / other: column already holds 0/1; Django will read them as int correctly.


def reverse_status_to_boolean(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute("""
            ALTER TABLE main_app_attendancereport
            ALTER COLUMN status TYPE boolean
            USING CASE WHEN status = 1 THEN TRUE ELSE FALSE END
        """)


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_group_archive_assignment_subject_optional'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    convert_status_to_smallint,
                    reverse_code=reverse_status_to_boolean,
                ),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='attendancereport',
                    name='status',
                    field=models.SmallIntegerField(
                        choices=[(0, 'Absent'), (1, 'Present'), (2, 'Late')],
                        default=0,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ResultFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='results/')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.group')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main_app.student')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.staff')),
            ],
            options={
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
