from django.db import migrations

def create_initial_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")  # Replace 'accounts' with your actual app name
    Role.objects.create(name="principal")
    Role.objects.create(name="manager")
    Role.objects.create(name="teacher")
    Role.objects.create(name="parent")
    Role.objects.create(name="student")

def delete_initial_roles(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(name__in=["superadmin", "principal", "teacher", "parent", "student"]).delete()

class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),  # Ensure this is the correct app name
    ]

    operations = [
        migrations.RunPython(create_initial_roles,delete_initial_roles),
    ]
