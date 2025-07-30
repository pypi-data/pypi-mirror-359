from django.db import migrations

def create_default_config(apps, schema_editor):
    GreenlightConfig = apps.get_model("greenlight", "GreenlightConfig")
    
    if not GreenlightConfig.objects.exists():
        GreenlightConfig.objects.create(
            name="default",
            green_message="🟢 **GREEN ALERT!** All clear.",
            yellow_message="🟡 **YELLOW ALERT!** Be ready.",
            red_message="🔴 **RED ALERT!** Action needed!",
        )

class Migration(migrations.Migration):

    dependencies = [
        ("greenlight", "0004_webhook_greenlightconfig"), 
    ]

    operations = [
        migrations.RunPython(create_default_config),
    ]
