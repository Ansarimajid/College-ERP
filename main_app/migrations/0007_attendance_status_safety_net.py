from django.db import migrations, models


def ensure_status_is_integer(apps, schema_editor):
    """
    Safety net: if migration 0006 was recorded as applied on PostgreSQL but the
    USING CASE WHEN clause never ran (e.g. the column was already integer, or the
    migration was faked), this is a no-op. If the column is still boolean, convert it.
    """
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT data_type
            FROM information_schema.columns
            WHERE table_name = 'main_app_attendancereport'
              AND column_name = 'status'
        """)
        row = cursor.fetchone()
        if row and row[0] == 'boolean':
            schema_editor.execute("""
                ALTER TABLE main_app_attendancereport
                ALTER COLUMN status TYPE smallint
                USING CASE WHEN status THEN 1 ELSE 0 END
            """)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0006_attendancereport_status_int_resultfile'),
    ]

    operations = [
        migrations.RunPython(ensure_status_is_integer, reverse_code=noop),
    ]
